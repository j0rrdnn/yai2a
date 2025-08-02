# YAI2A is an image to ASCII art generator program that allows you to convert any image into an ASCII art.
# Github: j0rrdnn

import argparse
import numpy as np
from PIL import Image, ImageEnhance

grayScale1 = r'$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~i!lI;:,\"^`". '
grayScale2 = '@%#*+=-:. '
grayScale3 = r'@&#*+=~-:,. '

def returnAverageScale(image):
    imageArray = np.array(image)
    imageWidth, imageHeight = imageArray.shape
    return np.average(imageArray.reshape(imageWidth*imageHeight))

def enhanceImage(image, contrast=1.2, brightness=1.0, sharpness=1.1):
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(contrast)
    
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(brightness)
    
    enhancer = ImageEnhance.Sharpness(image)
    image = enhancer.enhance(sharpness)
    
    return image

def resizeImage(image, max_width=200):
    width, height = image.size
    if width > max_width:
        ratio = max_width / width
        new_height = int(height * ratio)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)
    return image

def gammaCorrection(image, gamma=1.2):
    imageArray = np.array(image, dtype=np.float64)
    imageArray = 255 * (imageArray / 255) ** (1.0 / gamma)
    return Image.fromarray(imageArray.astype(np.uint8))

def convertImage(fileName, imgColumns, imgScale, moreLevels, enhance, gamma):
    global grayScale1, grayScale2, grayScale3
    
    dataImage = Image.open(fileName).convert('L')
    
    if enhance:
        dataImage = enhanceImage(dataImage, contrast=1.3, brightness=1.05, sharpness=1.2)
    
    if gamma != 1.0:
        dataImage = gammaCorrection(dataImage, gamma)
    
    dataImage = resizeImage(dataImage, max_width=300)
    
    imageWidth, imageHeight = dataImage.size[0], dataImage.size[1]
    
    imgColumns = min(imgColumns, imageWidth)
    
    dataWidth = imageWidth / imgColumns
    dataHeight = dataWidth * imgScale
    imgRows = int(imageHeight / dataHeight)
    imgRows = max(1, imgRows)
    
    print(f"Processed image size: {imageWidth}x{imageHeight}")
    print(f'columns: {imgColumns}, rows: {imgRows}')
    print(f'tile dims: {dataWidth:.1f} x {dataHeight:.1f}')
    
    if imgColumns > imageWidth or imgRows > imageHeight:
        print('Image too small for specified columns.')
        return
    
    asciiImg = []
    pixelValues = []
    
    for y in range(imgRows):
        yValue1 = int(y * dataHeight)
        yValue2 = int((y + 1) * dataHeight)
        
        if y == imgRows - 1:
            yValue2 = imageHeight
            
        asciiImg.append('')
        
        for x in range(imgColumns):
            xValue1 = int(x * dataWidth)
            xValue2 = int((x + 1) * dataWidth)
            
            if x == imgColumns - 1:
                xValue2 = imageWidth
                
            imageTile = dataImage.crop((xValue1, yValue1, xValue2, yValue2))
            averageL = int(returnAverageScale(imageTile))
            pixelValues.append(averageL)
    
    if len(pixelValues) > 0:
        minVal = min(pixelValues)
        maxVal = max(pixelValues)
        
        if maxVal > minVal:
            for i, val in enumerate(pixelValues):
                pixelValues[i] = int(255 * (val - minVal) / (maxVal - minVal))
    
    idx = 0
    for y in range(imgRows):
        for x in range(imgColumns):
            averageL = pixelValues[idx]
            idx += 1
            
            if moreLevels == 2:
                grayScaleValue = grayScale1[min(int((averageL * (len(grayScale1)-1)) / 255), len(grayScale1)-1)]
            elif moreLevels == 1:
                grayScaleValue = grayScale3[min(int((averageL * (len(grayScale3)-1)) / 255), len(grayScale3)-1)]
            else:
                grayScaleValue = grayScale2[min(int((averageL * (len(grayScale2)-1)) / 255), len(grayScale2)-1)]
                
            asciiImg[y] += grayScaleValue
            
    return asciiImg

def main():
    argsDescription = 'This program converts an image into ASCII art.'
    argsParser = argparse.ArgumentParser(description=argsDescription)
    
    argsParser.add_argument('--file', dest='imgFile', required=True)
    argsParser.add_argument('--scale', dest='imgScale', required=False, type=float, default=2.2)
    argsParser.add_argument('--output', dest='imgOutput', required=False)
    argsParser.add_argument('--cols', dest='imgColumns', required=False, type=int, default=100)
    argsParser.add_argument('--levels', dest='moreLevels', type=int, choices=[0, 1, 2], default=1, 
                           help='Character density: 0=simple, 1=medium, 2=complex')
    argsParser.add_argument('--enhance', action='store_true', help='Apply image enhancement')
    argsParser.add_argument('--gamma', type=float, default=1.2, help='Gamma correction (1.0-2.0)')
    
    argsCmd = argsParser.parse_args()
    
    imgFile = argsCmd.imgFile
    
    outputFile = 'output.txt'
    if argsCmd.imgOutput:
        outputFile = argsCmd.imgOutput
        
    imgScale = argsCmd.imgScale
    imgColumns = argsCmd.imgColumns
    
    print('Generating enhanced ASCII art...')
    print(f'Settings: cols={imgColumns}, scale={imgScale}, levels={argsCmd.moreLevels}, enhance={argsCmd.enhance}, gamma={argsCmd.gamma}')
    
    asciiImg = convertImage(imgFile, imgColumns, imgScale, argsCmd.moreLevels, argsCmd.enhance, argsCmd.gamma)
    if asciiImg is None:
        print("Conversion failed. Try using fewer columns or a larger image.")
        return
    
    with open(outputFile, 'w', encoding='utf-8') as writeFile:
        for imgRows in asciiImg:
            writeFile.write(imgRows + '\n')
    
    print(f'ASCII art has been written to: {outputFile}')
    
if __name__ == '__main__':
    main()