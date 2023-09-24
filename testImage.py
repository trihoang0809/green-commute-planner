from PIL import Image

# Open the WebP image
webp_image = Image.open("Season_2022_-_Bronze.webp")

# Save it as a PNG image
webp_image.save("output_image.png", "PNG")

# Close the image
webp_image.close()