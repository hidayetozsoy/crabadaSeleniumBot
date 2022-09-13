import os,sys
sys.path.append((os.path.dirname(__file__)))
from captchaSolver import find_image_in_captcha

CAPTCHA_IMAGES_PATH = "./captchaImages/" 

def resolveCaptcha(captchaId):
    folderUrl = CAPTCHA_IMAGES_PATH+captchaId
    captchaFolder = os.listdir(folderUrl)
    captchaFolder.sort()
    mainImg, q1, q2, q3 = captchaFolder[0], captchaFolder[1], captchaFolder[2], captchaFolder[3]
    with open(f"{folderUrl}/{mainImg}", "rb") as image:
        f = image.read()
        img = bytearray(f)
        
    with open(f"{folderUrl}/{q1}", "rb") as image:
        f = image.read()
        ans1 = bytearray(f)
        
    with open(f"{folderUrl}/{q2}", "rb") as image:
        f = image.read()
        ans2 = bytearray(f)
        
    with open(f"{folderUrl}/{q3}", "rb") as image:
        f = image.read()
        ans3 = bytearray(f)

    targets, icons_rect_coordinates, mapping = find_image_in_captcha(img, [ans1, ans2, ans3])
    if len(mapping) != 3:
        return False
    
    allPositions = dict()
    for key in range(1,4):
        x, y, w, h = icons_rect_coordinates[mapping[key-1]]
        # x,y is the coordinate of top left hand corner
        # Bounding box is 70x70, so centre of circle = (x+70/2, y+70/2), i.e. (x+35, y+35)
        centre_x = x+(w//2)
        centre_y = y+(h//2)
        allPositions[f"{key}"] = {"x":centre_x, "y":centre_y}
    return allPositions

if __name__ == "__main__":
    print(resolveCaptcha("c4c4f77dea9847a6a2d552ec064986dd"))