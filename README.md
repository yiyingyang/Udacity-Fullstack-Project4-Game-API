#Full Stack Nanodegree Project 4 Game API - Rock-paper-scissors

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
 You could also add any front end to this application.
 
 
 
##Game Description:

Rock-paper-scissors is a zero-sum hand game usually played between two people, 
in which each player simultaneously forms one of three shapes with an outstretched
hand. These shapes are "rock" (a simple fist), "paper" (a flat hand), and 
"scissors" (a fist with the index and middle fingers together forming a V). 
The game has only three possible outcomes other than a tie: a player who decides
to play rock will beat another player who has chosen scissors ("rock crushes scissors")
but will lose to one who has played paper ("paper covers rock"); a play of paper 
will lose to a play of scissors ("scissors cut paper"). If both players throw the
same shape, the game is tied.
 
While playing, the player will make his choice in "rock", "paper" and "scissors",
and the app will randomly generate a choice as the player's opponent. The result
will be showed to the player immediately.Each game can be retrieved by using the
path parameter `urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, player_choice
    - Returns: GameForm with game result.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. A valid choice of in
    "rock", "paper" and "scissors" has to be made - will raise BadRequestException
    if not. The app will randomly generate a choice as the player's opponent. The
    result will be returned as a GameForm. The user record of 'wins', 'loses', 
    'games' and 'win_ratio' are updated.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with game state.
    - Description: Returns the state of a game.
    
 - **get_all_users**
    - Path: 'allusers'
    - Method: GET
    - Parameters: None
    - Returns: UserForms of all users.
    - Description: Returns UserForms of all users.
    
 - **get_user_record**
    - Path: 'record/{user_name}'
    - Method: GET
    - Parameters: user_name, email (optional)
    - Returns: UserForm of a specific user.
    - Description: Returns UserForm of a specific user.
    
 - **get_all_games**
    - Path: 'allgames'
    - Method: GET
    - Parameters: None
    - Returns: GameForms of all games.
    - Description: Returns GameForms of all games.
    
 - **get_user_games**
    - Path: 'games/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms of a specific user.
    - Description: Returns GameForms of a specific user.

 - **get_user_rankings**
    - Path: 'rankings'
    - Method: GET
    - Parameters: None
    - Returns: RankForms of all users ordered by win_ratio.
    - Description: Returns RankForms of all users ordered by win_ratio.

 - **get_top_ten**
    - Path: 'topten'
    - Method: GET
    - Parameters: None
    - Returns: StringMessage of top ten ranking by win_ratio.
    - Description: Return top ten ranking.
    

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's result (urlsafe_key, player_choice, pc_choice,
    result, message, user_name).
 - **NewGameForm**
    - Used to create a new game (user_name, player_form)
 - **UserForm*
* 	- Representation of a User's record(user_name, win_ratio, games, wins, loses,
 	draws)
 - **RankForm**
    - Representation of a User's ranking record (user_name, win_ratio)
 - **StringMessage**
    - General purpose String container.
 - **GameForms**
    - Multiple GameForm container.
 - **UserForms**
    - Multiple UserForm container.
 - **RankForms**
    - Multiple RankForm container.