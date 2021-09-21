# Twitter NLP Analysis Models

created by Robert Gramlich

![Twitter Sentiment Image](https://miro.medium.com/max/1400/1*0P55fknrgWKxG0gfwAGCvw.png)

<!-- TABLE OF CONTENTS -->
<details open="open">
  <summary><h2 style="display: inline-block">Table of Contents</h2></summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

## Project Description

The NLP Analysis Model project aims to create a series of neural networks that can predict the sentiment, or lack of sentiment, for tweets from Twitter. The first model is trained, tested, and validated on a IMDB movie reviews dataset with prescribed positive or negative rankings. This model will have its metrics tested to determine the validity of using non twitter contexualized data.  The sequential models following the data collection process will be an NLP adjudication model, and pure Twitter data model, and a composite model of twitter and rewiew data. The purpose of the adjudication model is to act as a filter for non sentiment related language such as advertisements, AI's, and descriptive language. The pure twitter model, like the composite model, exists to test the various models against each other based upon their data used. 

My NLP Analysis application includes a level of interactivity through Flask and JavaScript D3. Each tweet that is classified by the user is then pushed along with the classification and time stamp into an AWS RDS Postgresql database. Also stored are the various metrics used to benchmark the success of these models such as ROC data, AUC data, precision, and recall.  Also stored in the database are all the various models and their vectorizers in a pickle bytea format. I have also included the version numbers for all the models along with all the id's used in the train test split so any model's components may be analyzed from every angle as well as be rebuilt. I've further created logic to test how the versions performed during their batch epochs and stored the metrics as well.



## Data

* [IMDB Movie Review Dataset](http://ai.stanford.edu/~amaas/data/sentiment/) -- Citation: Maas, Andrew L., et al. “Learning Word Vectors for Sentiment Analysis.” Proceedings of the 49th Annual Meeting of the Association for Computational Linguistics: Human Language Technologies, June 2011, pp. 142–150., www.aclweb.org/anthology/P11-1015. 

* [Twitter API](https://developer.twitter.com/en/docs)

### Built With

* PostgreSQL/SQLAlchemy
* Pandas - tensorflow
* Flask
* HTML
* JavaScript - D3

<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Installation

1. Clone the repo
   ```sh
   git clone https://github.com/sunwoo-kim20/sentiment-analysis-final-project.git
   ```
2. Set up PostgreSQL database and establish connection 
   ```sh
   rds_connection_string = "user:password@{AWS server}:5432/sentiment_db"
   engine = create_engine(f'postgresql://{rds_connection_string}')
   conn = engine.connect()
   session = Session(bind=engine)
   ```



<!-- USAGE EXAMPLES -->
## Usage

User grabs a tweet by giving the keyword selection an input. Once the tweet has been loaded onto the webpage, the user selects whether they consider the tweet to be neutral, positive, or negative in sentiment. Based upon the sum of data collected, various models will make predictions.  The adjudication model will always make a prediction. The other models however will only make predictions if the tweet is declared to have sentiment. I feel it illogical to use resources predicting sentiment on a tweet that has none. 

![Screenshot of Sentiment Analysis Application](https://github.com/sunwoo-kim20/sentiment-analysis-final-project/blob/main/static/images/voting_page.png?raw=true)


![Screenshot of Neural Network Structure](https://github.com/sunwoo-kim20/sentiment-analysis-final-project/blob/main/static/images/the_model.PNG?raw=true)



<!-- CONTACT -->
## Contact


[Project Link](https://github.com/PopeStarkiller/NLP)

