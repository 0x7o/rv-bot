import os
import time
import random
import requests
from PIL import Image
from gradio_client import Client
from transformers import pipeline

client = Client("0x7o/RussianVibe", hf_token=os.environ.get("HF_TOKEN"))
prompt_pipe = pipeline("text-generation", model="openai-community/gpt2")

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
    prompt = prompt_pipe("""1. The image features a beautiful pink and purple sky, with a tree and a streetlight in the foreground. The sky is filled with a pink hue, and the tree and streetlight are situated at the bottom of the image.

2. The image features a tall apartment building with many windows. The building is made of brick, and it appears to be in a state of disrepair.

3. The image features a large white building situated on a hill overlooking a river. A boat is visible in the water, floating near the shore. The building is surrounded by trees, creating a serene and picturesque scene. The sky is overcast, adding a sense of tranquility to the scene.

4. The image features a""", do_sample=True, temperature=0.7, max_new_tokens=75)[0]["generated_text"]
    prompt = prompt.split("4. The image features a")[0].split("\n")[0]
    return f"The image features a{prompt}"


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
