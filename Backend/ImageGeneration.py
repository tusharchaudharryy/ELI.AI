import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import get_key
from pathlib import Path
import os
from time import sleep

# Get paths
current_path = Path(__file__).resolve()
root_path = current_path.parents[1]  # ELI.AI folder
env_path = root_path / ".env"
data_file_path = root_path / "Frontend" / "Files" / "ImageGeneration.data"
image_save_folder = root_path / "Data"

# Create image folder if it doesn't exist
image_save_folder.mkdir(parents=True, exist_ok=True)

# Load API key from .env
headers = {
    "Authorization": f"Bearer {get_key(str(env_path), 'HuggingFaceAPIKey')}"
}
API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-2-1"

# Function to open generated images
def open_images(prompt):
    prompt = prompt.replace(" ", "_")
    files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in files:
        image_path = image_save_folder / jpg_file
        try:
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)
        except IOError:
            print(f"Unable to open {image_path}")

# Async request to Hugging Face
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    if "image" in response.headers.get("Content-Type", ""):
        return response.content
    else:
        print("Error from API:", response.text)
        return None

# Generate 4 images asynchronously
async def generate_images(prompt: str):
    tasks = []
    for _ in range(4):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, Ultra High details, high resolution, seed={randint(0, 1000000)}"
        }
        tasks.append(asyncio.create_task(query(payload)))

    image_bytes_list = await asyncio.gather(*tasks)

    for i, image_bytes in enumerate(image_bytes_list):
        if image_bytes is None:
            continue
        image_file = image_save_folder / f"{prompt.replace(' ', '_')}{i + 1}.jpg"
        with open(image_file, "wb") as f:
            f.write(image_bytes)

# Main image generation wrapper
def GenerateImage(prompt: str):
    asyncio.run(generate_images(prompt))
    open_images(prompt)

# File watcher loop
while True:
    try:
        with open(data_file_path, "r") as f:
            Data = f.read().strip()

        Prompt, Status = Data.split(",")

        if Status.strip() == "True":
            print("Generating Image...")
            GenerateImage(prompt=Prompt)

            with open(data_file_path, "w") as f:
                f.write("False,False")
            break
        else:
            sleep(1)

    except Exception as e:
        print("Error:", e)
        sleep(1)