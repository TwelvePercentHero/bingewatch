# Binge | Watch - Data Centric Development Milestone Project
This is an app designed to help people create their ideal movie night by combining collections of recipes and media such as film, TV and video games, and creating pairings and recommendations across the two collections. The app is also designed to allow users to register and login in order to create, edit and delete recipes and media records to allow them to contribute to the database and community.

## UX
My goal in the design and development of the app was to create a visually engaging and accessible way of storing and surfacing information relating to both recipes and media, as well as a place for users to build their own database of preferences for easy access in the future.

I also wanted to create a secure app, both in terms of the storage of user information and ensuring that access to certain functions was restricted to users only. This required a user login function to control access to certain pages, which was not something I had initially factored into the design and early development of the site. If I was to start the project from scratch, the user login would likely be one of the first functions that I would have included as it factors in to a number of the other functions included within the app - this would have saved time refactoring code at a later stage of the project.

It was also important that the app was responsive and easy to access and use on mobile devices, as it would be useful for users to be able to access lists of ingredients while they are shopping in the supermarket, for example. As such I ensured that the design of the app was mobile-first, and each design aspect was thoroughly tested on multiple virtual devices using Google Developer Tools.

I looked at existing recipe sites and apps for inspiration around the design and development of my own app, including [Food52](https://food52.com/ "Food52 homepage") which is built around creating a user-generated community of cooks and recipes, and the [BBC Good Food](https://www.bbcgoodfood.com/ "BBC Good Food homepage"), which I personally use on a regular basis and find easy to access.

I also looked at the Internet Movie Database or [IMDB](https://www.imdb.com/ "IMDB homepage") to understand the key pieces of information that people may search when looking for a film recommendation. This heavily informed the development of the media collection within my database, as I wanted to ensure that the key data was included.

A series of **User Stories** can be found in the user-stories.md file.

A set of wireframes can be found in the wireframes folder, mocked up using [Balsamiq](https://balsamiq.com/ "Balsamiq homepage"). The final design of the app remained largely similar to these mockups with a few small changes based on functionality.

## Technologies
I used the following technologies within my app.

- [Python3](https://www.python.org/ "Python homepage")
    - I used Python3 to develop all backend code and functions.
- [Flask](https://palletsprojects.com/p/flask/ "Flask documentation")
    - The Flask micro-framework was used to speed up development of the Python app and to construct and render pages.