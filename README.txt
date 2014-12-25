This is very basic utility for facebook moderation automation.

Disclaimer: This tool was written as quick hack for one simple task,
w/o any generalization in mind.

Motivation. Lets assume you have just create public event. And it
becomes very popular. Almost immidietly crazy users appears and
start to post thousands of sapm comments, pictures and etc. Such
activity make page unreadable. So admin have to bad and remove
bad comments one by one Such technique is not effective and errore
prone. This tool helps one to optimize bad comments removals. One simply
have to add user to black list. Later all comments from users from bad
list will be removed.

Original motivation is to help to protect the "15.1.15" event in Russia
from spam bots.

Requires: https://github.com/pythonforfacebook/facebook-sdk

Stage (0) Obtain oauth key from facebook
     Please visit https://developers.facebook.com/tools/explorer/
     Push button "Get access token"
     toggle "public_actions" radio button on 'Extended permissions' dialog
     And then press 'Get access token button' inside that dialog
     Copy paste string from 'Access Token' to notepad
     Alternative way to use following guide http://smashballoon.com/custom-facebook-feed/access-token/


Stage (1) Initialization:
      Lets pretent your access toke is "CAACEdEose0cBAAqa2HcFyW73n8cBItvyF9qPT"
      And your event id is 417200101767938 (Id of 15.1.15)

      # Copy paster this to your console (DO NOT FORGET TO INSERT YOUR ACTUAL ACCESSTOKEN )
      python ./fb-sanitizer.py -v -C -i 417200101767938 -k CAACEdEose0cBAAqa2HcFyW73n8cBItvyF9qPT

Stage (2) fetch feed cache from facebook
      # run following commend
      python ./fb-sanitizer.py -v  -U

Stage (3) Add user to black list
      In order to add user to black list you need it's USER ID. Simplest way to add it
      is to pont mouse to 'time' list of one of it's comments to the. The one which near 'Like'
      For example My comments looks like follows:
      Dmitry Monakhov GO go GO!!!
      37 mins · Like
      You have to click on "37 mins" link. Browser will open that link. It will looks like follows
      https://www.facebook.com/events/503655129774093/permalink/503655133107426/?comment_id=504265043046435
      The most important part is "comment_id=504265043046435"

      All you have to do is to add this object_id like follows:
      #python ./fb-sanitizer.py -v  -O 504265043046435
      
      One can repeat this procedure many times and add as many bad users as necessery.

Stage (4) Remove comments for  each user from black list
      #python ./fb-sanitizer.py -v  -U -R 


     
