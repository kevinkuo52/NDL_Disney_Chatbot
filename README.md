# NDL_Disney_Chatbot

## HakunamaBOT (Lion King Personality Chatbot)

This project is a retrieval-based chatbot, centered on two characters of Lion King: "Simba" and "Scar".

It is implemented on Slack, and ideally, we can implement it on the website we created: [hakunamabot.com](http://hakunamabot.com/)

## Functionalities of the chatbot:

-Starting point: user picks the character between "Simba"(teenager) and "Scar";

-User message to the chatbot, use @hakuna_ma_bot_a to trigger, then the bot takes certain keywords (that we have generated) and replies;

-Replies are tailored to the personality chosen, and personalities are based on the movie script;

-Some answers given by the bot have more than one possible answer, so the response is randomized;

-Some Q&A are more than one layer of the decision tree

## Credit:
we pulled tf_idf.py and previous_chats.json from https://github.com/vaibhavgeek/retrieval-based-chatbot and edited it for our project 
