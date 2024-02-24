import os
import time
import random
import requests
from PIL import Image
from gradio_client import Client

client = Client("0x7o/RussianVibe", hf_token=os.environ.get("HF_TOKEN"))

VK_TOKEN = os.environ.get("VK_TOKEN")
VK_GROUP_ID = os.environ.get("VK_GROUP_ID")


def make_post(image: Image, message: str):
    image.save("temp.png")
    upload_url = requests.get(
        "https://api.vk.com/method/photos.getWallUploadServer",
        params={"access_token": VK_TOKEN, "group_id": VK_GROUP_ID, "v": "5.199"},
    ).json()["response"]["upload_url"]
    upload = requests.post(
        upload_url,
        files={"photo": open("temp.png", "rb")},
    ).json()
    photo = requests.get(
        "https://api.vk.com/method/photos.saveWallPhoto",
        params={
            "access_token": VK_TOKEN,
            "group_id": VK_GROUP_ID,
            "v": "5.199",
            "server": upload["server"],
            "photo": upload["photo"],
            "hash": upload["hash"],
        },
    ).json()
    photo = photo["response"][0]
    requests.get(
        "https://api.vk.com/method/wall.post",
        params={
            "access_token": VK_TOKEN,
            "owner_id": f"-{VK_GROUP_ID}",  # keep the negative sign here
            "from_group": 1,
            "attachments": f"photo{photo['owner_id']}_{photo['id']}",
            "message": message,
            "v": "5.199",
        },
    )
    os.remove("temp.png")


def generate(prompt, w=1024, h=1024) -> Image:
    result = client.predict(
        prompt,  # str  in 'Prompt' Textbox component
        "low quality, painting, bad architecture, artifacts, inscriptions, bad anatomy, distortions, ugliness, mutations",
        "",  # str  in 'Prompt 2' Textbox component
        "",  # str  in 'Negative prompt 2' Textbox component
        True,  # bool  in 'Use negative prompt' Checkbox component
        False,  # bool  in 'Use prompt 2' Checkbox component
        False,  # bool  in 'Use negative prompt 2' Checkbox component
        random.randint(
            0, 2147483647
        ),  # float (numeric value between 0 and 2147483647) in 'Seed' Slider component
        w,  # float (numeric value between 256 and 1536) in 'Width' Slider component
        h,  # float (numeric value between 256 and 1536) in 'Height' Slider component
        5,  # float (numeric value between 1 and 20) in 'Guidance scale for base' Slider component
        5,  # float (numeric value between 1 and 20) in 'Guidance scale for refiner' Slider component
        30,  # float (numeric value between 10 and 100) in 'Number of inference steps for base' Slider component
        25,  # float (numeric value between 10 and 100) in 'Number of inference steps for refiner' Slider component
        True,  # bool  in 'Apply refiner' Checkbox component
        api_name="/run",
    )
    return Image.open(
        requests.get(
            f"https://0x7o-russianvibe.hf.space/file={result}", stream=True
        ).raw
    )


def generate_city_prompt():
    prompt = """1. The image features a large apartment building with several windows, illuminating the scene with warm light. The building is situated in a snowy area, with snow-covered trees and a street in the foreground. The snow is falling, creating a beautiful and serene atmosphere.

2. The image features a large apartment building at dusk, with many windows lit up. The building is situated on a street, and the windows are illuminated by the setting sun. The scene is quite dramatic, with the building's facade illuminated by a warm glow from the sun.

3. The image features a beautiful sunset over a cityscape with tall buildings. The sky is filled with pink and orange hues, creating a vibrant and captivating atmosphere. The sun is setting behind the buildings, creating an impressive and dramatic scene. The cityscape is dominated by the large apartment buildings, with some of them appearing closer to the foreground and others further back. The combination of the sunset and the cityscape creates a visually appealing and captivating scene.

4. The image features a"""
    res = requests.post('https://api.together.xyz/v1/completions', json={
        "model": "meta-llama/Llama-2-13b-hf",
        "max_tokens": 1572,
        "prompt": prompt,
        "temperature": 0.7,
        "top_p": 0.7,
        "top_k": 50,
        "repetition_penalty": 1,
        "stop": [
            "\n", "5."
        ],
        "update_at": "2024-02-22T11:05:46.153Z"
    }, headers={
        "Authorization": "Bearer " + os.environ.get("TOGETHER_API_KEY")
    })
    return "The image features a " + res.json()["choices"][0]["text"].strip()


def main():
    while True:
        prompt = generate_city_prompt()
        print(f"Prompt: {prompt}")
        try:
            image = generate(prompt)
            print("Generated image")
            make_post(image, "#thisrussiadoesnotexist")
            print("Posted to VK")
            print(f"Sleeping for some hour...")
            time.sleep(3600 + random.randint(0, 600))
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)


if __name__ == "__main__":
    main()
