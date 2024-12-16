import os
import json
import random
from faker import Faker

image_directory = "A:/Tugas/Algeo/mydataset/pict"
output_file = "mapper-v2.json"

audio_files = [
    "Billie_Jean.mid",
    "Blue_Christmas.mid",
    "Cant_Help_Falling_in_Love.mid",
    "Come_as_You_Are.mid",
    "Dont_Forget_to_Remember.mid",
    "Heal_The_World.mid",
    "Heart-Shaped_Box.mid",
    "Hey_Jude.1.mid",
    "Hey_Jude.mid",
    "Holiday.mid",
    "Hotel_California_unplugged_.mid",
    "How_Can_You_Mend_a_Broken_Heart.2.mid",
    "How_Deep_Is_Your_Love.4.mid",
    "In_My_Life.mid",
    "Isnt_She_Lovely.5.mid",
    "Isnt_She_Lovely.mid",
    "Jive_Talkin.mid",
    "Let_It_Be.mid",
    "Love_You_Inside_Out.mid",
    "More_Than_a_Woman.mid",
    "Never_Gonna_Give_You_Up.mid",
    "New_York_Mining_Disaster_1941.2.mid",
    "Nights_on_Broadway.1.mid",
    "Night_Fever.2.mid",
    "Rock_With_You.mid",
    "Smells_Like_Teen_Spirit.mid",
    "Stayin_Alive.mid",
    "Too_Much_Heaven.3.mid",
    "Yesterday.mid",
    "You_Win_Again.1.mid"
]

images = [img for img in os.listdir(image_directory) if img.endswith(".jpg")]

fake = Faker()

def generate_unique_name():
    num_words = random.randint(1, 3)
    name_parts = [fake.word() for _ in range(num_words)]
    return " ".join(name_parts)

json_data = []
for i, img in enumerate(images):
    audio_file = audio_files[i % len(audio_files)]
    unique_name = generate_unique_name()
    json_data.append({
        "name": unique_name,
        "audio_file": audio_file,
        "pic_name": img,
    })

with open(output_file, "w") as f:
    json.dump(json_data, f, indent=2)

print(f"JSON created: {output_file}")
