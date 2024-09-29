import os

import torch
from PIL import Image
import open_clip

# print(open_clip.list_pretrained())


from pprint import pprint

dvc = "cuda" if torch.cuda.is_available() else "cpu"

model, _, preprocess = open_clip.create_model_and_transforms('ViT-B-32', pretrained='laion2b_s34b_b79k', device=dvc)
print(f"model created")
model.eval()  # model in train mode by default, impacts some models with BatchNorm or stochastic depth active
tokenizer = open_clip.get_tokenizer('ViT-B-32')

imgDir = '/media/pbu/T7/dropbox-24-09/'
imgDir = "C:\\Users\\User\\Documents\\raspberry\\file-browser-imgs"
img1 = os.path.join(imgDir, 'berlin-1974-balkon-weissensee-holzbaukloetze.jpg')


tags = [
    "a stout woman with dark hair",
    "a man with black hair",
    "a child with blonde hair",
    "a boy   with blonde hair",
    "a boy   with brunette hair",
    "a person",
    "a boy",
    "a car",
    "a tree",
    "a house",
    # "a table",
    # "a chair",
    "a monochrome image",
]


tagsTokenized = tokenizer(tags)


# single img
imgPreprocessed = preprocess(Image.open(img1)).unsqueeze(0)
with torch.no_grad(), torch.cuda.amp.autocast():
    imagFeats  = model.encode_image(imgPreprocessed)
    textFeats  = model.encode_text(tagsTokenized)
    imagFeats  /= imagFeats.norm(dim=-1, keepdim=True)
    textFeats  /= textFeats.norm(dim=-1, keepdim=True)

    textProbs = (100.0 * imagFeats @ textFeats.T).softmax(dim=-1)

# print("Label probs:", textProbs)

print(f"textProbs type {type(textProbs)}")

try:
    for idx1, torchTens1 in enumerate(textProbs):
        for idx2, torchTens2 in enumerate(torchTens1):
            prob = torchTens2.item()
            if prob > 0.2:
                print(f"{idx2:2}  Tag: {tags[idx2]:<32} - {prob:10.4f}")
except Exception as e:
    print(e)




def tagImgs(imgDir, mdl, preprocess, txtInps):

    print(f"\t listdir start")

    for imgFile in os.listdir(imgDir):

        try:

            if imgFile.lower().endswith(('.png', '.jpg', '.jpeg')):

                imgPath = os.path.join(imgDir, imgFile)
                img = preprocess(Image.open(imgPath)).unsqueeze(0).to(dvc)

                print(f"\t {imgPath} start")

                with torch.no_grad(), torch.cuda.amp.autocast():
                    imagFeats  = model.encode_image(img)
                    textFeats  = model.encode_text(tagsTokenized)
                    imagFeats  /= imagFeats.norm(dim=-1, keepdim=True)
                    textFeats  /= textFeats.norm(dim=-1, keepdim=True)

                    textProbs = (100.0 * imagFeats @ textFeats.T).softmax(dim=-1)

                for idx1, torchTens1 in enumerate(textProbs):
                    for idx2, torchTens2 in enumerate(torchTens1):
                        prob = torchTens2.item()
                        if prob > 0.2:
                            print(f"{idx2:2}  Tag: {tags[idx2]:<32} - {prob:10.4f}")

        except Exception as e:
            print(f"problem with {imgFile}")
            print(e)


tagImgs(imgDir, model, preprocess, tagsTokenized)
