# USF_JETT
Hello Everyone!!
Canvas JETT

Contributors: **Jesse Simmons, Ethan Vasquez, Temirzhan Mukhambet, Tommy Le**

About:
JETT is our submission for the HackUSF 2025 Canvas Web API track
JETT utilizes Microsoft Azure custom vision and computer vision with python to detect the occupancy of a room.
We trained the AI model to detect where tables and people were and gave an overall percentage of busyness.


Software / Utilities:
Python, Microsoft Azure, Javascript, CSS, HTML

Necessary packages:
Because we aren't hosting, to run our project you'll need to manually download the PIP packages from your terminal. The list of them are down below:

pip install fastapi uvicorn
pip install azure-cognitiveservices-vision-customvision
pip install azure-cognitiveservices-vision-computervision
pip install azure-ai-formrecognizer
pip install msrest

Devpost:
## Inspiration
We took inspiration from the presentation given by Buck Woody in the use of Azure AI.

## What it does
The first AI (CAM) was trained to detect occupied tables and identify availability.
The second AI (MAP) was a preset, Computer Vision, and was used to detect the distance two relative points on the campus map.
Our back-end then takes these values to the front and displays the data in 2 unique presets:
1. A bar of low, medium and high occupancy with colors green, yellow, and red, respectively.
2. A percentage of the total people identified by the AI are divided by the amount of seats in a given room.
We also have 3 additional features:
- Student study room booking
- The location to the nearest available study room feature; according to the schedule of the user**
(TIME SPECIFIC: The schedule of the user obtained via the database)
- Photo upload feature (Try it on a non-preset room!)

## How we built it
We trained 2 AI's, Custom Vision AI and Computer Vision AI. Utilized python to connect our back-end to the data processed by the AI. We then used React, HTML, Tailwind CSS and Javascript to visualize the data in the frontend.

## Challenges we ran into
Azure was a brand new concept to our team. Being first time hackathon participants we ran into challenges and learning curves in the implementation of the AI.
## Accomplishments that we're proud of
It runs! The fact that all of us are new to hackathons we were able to produce a working application. We are extremely proud of JETT!
## What we learned
We learned extensively about the ins and outs of how Azure AI connects to different coding languages and frameworks, along with how to effectively use Git and Github.
## What's next for JETT
JETT is definitely in its early stages and plans for the future are vast. To name a few things we hope to push for in the future being:
- A fully functional chrome extension with canvas integration
- Implement another AI to better scan the schedules and allow for photo upload
- Using user location to show the nearest study space
- Train the AI further better detect objects
- Not be limited to the 4 buildings given via presets (Additional campuses included)

This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app).