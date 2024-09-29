'''
# on raspberry
python3 -m venv ~/imgprocessing
source ~/imgprocessing/bin/activate
cd /media/pbu/T7/dropbox-24-09/google-takeout-2029-09
deactivate

# everywhere
pip install torch torchvision ftfy regex tqdm
pip install transformers
pip install git+https://github.com/openai/CLIP.git

# alternative
#  crashed the py at model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k')
pip install open_clip_torch


'''

print("loading libs  start")

import os
import torch
import clip
from PIL import Image
from torchvision import transforms
from transformers import CLIPProcessor, CLIPModel


print("loading model start")

model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")

print("loading processor start")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


# Load the CLIP model
device = "cuda" if torch.cuda.is_available() else "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)
print("loading stop")



# Directory containing the images
imgRoot = '/media/pbu/T7/dropbox-24-09/'

imgPath = os.path.join(imgRoot, 'google-takeout-2029-09', 'Photos')

imgPath = os.path.join(imgRoot, 'img', 'iche-1975-bis')


tags = [
    "a stout woman with dark hair",
    "a man with black hair",
    "a child with blonde hair",
    "a boy   with brunette hair",
    "a person", 
    "a boy", 
    "a car", 
    "a tree", 
    "a house", 
    "a table", 
    "a chair", 
    "monochrome image", 
]

# Encode the tag descriptions using CLIP
text_inputs = clip.tokenize(tags).to(device)


# Preprocess and tag images
def tagImgs(imgDir, mdl, preprocess, txtInps):

    print(f"\t listdir start")

    for imgFile in os.listdir(imgDir):

        if imgFile.endswith(('.png', '.jpg', '.jpeg')):

            # Load and preprocess the image
            imgPath = os.path.join(imgDir, imgFile)
            img = preprocess(Image.open(imgPath)).unsqueeze(0).to(device)

            print(f"\t {imgPath} start")

            # Perform inference with CLIP
            with torch.no_grad():
                imgFeatures = mdl.encode_image(img)
                txtFeatures = mdl.encode_text(txtInps)

                # Normalize features
                imgFeatures /= imgFeatures.norm(dim=-1, keepdim=True)
                txtFeatures /= txtFeatures.norm(dim=-1, keepdim=True)

                # Calculate similarity between image and text tags
                similarity = (100.0 * imgFeatures @ txtFeatures.T).softmax(dim=-1)

                # Get the most likely tags for the image
                values, indices = similarity[0].topk(5)  # Top 5 most likely tags
                
                for value, index in zip(values, indices):
                    cf = value.item()
                    if cf > 0.25:
                        print(f"\t     Tag: {tags[index]:<32} (Confidence: {cf*100:5.2f}%)")


tagImgs(imgPath, model, preprocess, text_inputs)
