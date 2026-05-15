# Desktop Pet

It's an interesting desktop pet app for your own baby~~~.



# Installation and preparation
## Environment Configuration
```aiignore
conda create -n desktop_pet python=3.10
pip install PyQt6
```
## Image/ Video preparation

- add your own pets' images/.gif to the images/
- The name of the file can be XXX-1.jpg...., you can choose one image as the startup image named to XXX - **1**.[format]
- The supported format is ['*.png', '*.jpg', '*.jpeg', '*.gif']

# Run

```aiignore
main.py
```

# Function
## Wake Word
- When the app start, your pets will talk to you.

## Interact
- You can touch your pet and she/he will give feedback.
- You can add the thing that your pet likes in the **mouse/** (must in .png format), and when your mouse on your pet, magic happened!
- Your pet will hide if you don't interact with it for 15s. You can add interesting images, such as tails, to the **tails/** (must in .png format) to customize what is displayed when the pet hides. 

## Change name
- You can right-click your pet and change the name to get your own baby.


# To be continued...

