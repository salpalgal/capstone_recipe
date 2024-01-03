# Recipe App
Recipe App is created with a thought of using up leftover ingredients from the fridge. Users can find recipes based on ingredients input on this app and save as favorites for the future. 
## Features
nav bar that contains:
- sign up
  - creates user in database
- log in/out
  - authentication that only allows access to users in database
  - data from interaction with app is specfic to each user 
- root page
  - landing page for the public 
- homepage
  - home page once logged in to chose where to go 
- drop down menu for search and results
  - drop down menu groups related categories together
  - search recipe form takes input values from user to backend
  - results diplays data from api to users as cards that can take them to details page of all the information associated with that link
  - each card contains a button for adding to favorites list  
- user profile
  - profile image and edit button to edit user information
  - displays user's favaoried recipes
  - each recipe contains button to remove that recipe from favorite list  
## User Flow
From the landing site, users can either sign up to create a new user or log in to existing account. Once logged in, the user will come to the homepage. From here, user will have full access to the nav bar options. Users can search for new recipes by clicking on the search button that will take them to the search form. Once submitted, the results will be displayed on results page. The displayed recipe cards will take users to recipe details page if they are interested in that recipe, as well as, a button to save the recipe to favorites list. The user profile is where the user can view and manage their favorites list. If user wish to edit their account information, the profile edit button on the profile page is where they should go. To logout, click on logout button. Once again, user will be back to the landing page.
## Links
- [spoonacular api](https://spoonacular.com/food-api/docs#Authentication)
- [site url]()
## Technology 
- python flask
- postgresql
- wtforms
- bootstrap
