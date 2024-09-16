from django.shortcuts import render, redirect
from pymongo import MongoClient
from openai import OpenAI
from pydantic import BaseModel

TICKETS = {'RIOT', 'ACMR'}

class StockSentiment(BaseModel):
    score: int
    reasoning: str
    ticket: str


def get_articles(ticket):
        client = MongoClient("mongodb://peppa:peppa@localhost:27017")

        db = client.stock_test  # 'stock_test' is the database name
        collection = db.articles_test  # 'articles_test' is the collection name

        # Query to find documents with ticket "RIOT" and limit to 3 results
        query = {"ticket": ticket}
        articles = collection.find(query).limit(3)
        
        return articles


def get_sentiment(articles, ticket, format):
    openai_message = f'''
    Below, you'll find articles about the stock {ticket}. Analyze them and give a score to the stock sentiment from 1 to 100.
    Write a comprehensive and thorough reasoning explaining the why of your score. Here are the articles: \n\n
    '''

    for article in articles:
        openai_message += article['article_body'] + '\n\n'
    client = OpenAI()
    
    completion = client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You're now the best stock analyzer."},
            {"role": "user", "content": openai_message}
        ],
        response_format=format
    )
        
    return completion.choices[0].message.parsed
    

def home_view(request, *args, **kwargs):
    sentiment = None
    error_msg = None
    if request.method == 'POST':
        user_input = request.POST.get('user_input')
        
        if user_input.upper() in TICKETS:
            ticket = user_input.upper()
            articles = get_articles(ticket)
            
            sentiment = get_sentiment(articles, ticket, StockSentiment)
            sentiment.ticket = ticket
        
            # Store the sentiment in session
            request.session['user_input'] = sentiment.__dict__
            
            # Redirect to the same view to prevent re-submission
            return redirect('home')
        else:
            error_msg = 'The ticket is not present in our database yet :('
            request.session['user_input_error'] = error_msg
    
            return redirect('home')
    
    sentiment = request.session.pop('user_input', None)
    error_msg = request.session.pop('user_input_error', None)
        
    return render(request, "home.html", {'user_input': sentiment, 'user_input_error': error_msg})
