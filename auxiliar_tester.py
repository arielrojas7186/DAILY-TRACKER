
"""
This file is meant to  be as a tester before set  the file  into its final  folder.
"""



from fastapi import FastAPI
from datetime import datetime , date as d
from connection_db import initialize_connection


class ScoreNotInRange(Exception):

     pass

class QuestionIDNotInRange(Exception):
     pass



#app=FastAPI()


# 1 change the way that  the data retrive the questions + its layers.
def enter_question_in_db(conn):
     cursor=conn.cursor()
     
     while True:
                 
          try:

                 for i in ['1) Conding ',  '2) English ' , '3) Internal Confidence ', '4) Social Courague ' , '5)  Social Skills ' , '6) Romantic ' , '7) Business ']:
                       print(i)
                 number=int(input("Enter your option= "))

                 if number < 1 or number > 7:
                       raise ScoreNotInRange
     
                 question=input("Enter here the question: ").strip().lower()
                 
                 cursor.execute("select id from layers where id = %s " , (number , ))
                 
                 lawyer_id=cursor.fetchone()
                 
                 cursor.execute("insert into questions (layer_id , question) values (%s , %s )" , (lawyer_id[0], question))
                 
                 conn.commit()
          except ValueError:
               print('Enter a valid number ')
               continue
          except TypeError :
                    print("Probably worng id ")
                    continue
          except ScoreNotInRange:
                print("The number was not between 1 & 7 ")
          
          except EOFError:
               print('Leaving the program ')
               break


def query_questions(connection):
     cursor=connection.cursor()
     cursor.execute('''select l.layer , q.id , q.question  from   questions q   join layers l on l.id=q.layer_id ''')
     lista=cursor.fetchall()
     
     
     dih={}
     for layer , id , question in lista:
          if layer not in dih:
                dih[layer]=[]
          dih[layer].append({'id':id , 'question': question})

     # dictionaries with list in its vaues and dicts inside the elements

     return dih


     """
     Format:
     dih={ layer : [{id :  }]}
     """



def get_layers ():

     return [ 'social_skills','romantic','competence','coding','english','internal_confidence','social_courage']
     
    



def enter_score_input(dih , cursor , dia ):
     value=True
     id=dih['id']
     
     score=input(f"{dih['question']} :")
     
     if score == 'n' or score == "N":
                         value=False
                         score=0.0
     else:
          if  score:
                         
               score=float(score) 
          else:
                score= 0.0

          if score >1.0 :
               raise ScoreNotInRange
          elif score < 0.0 :
               raise ScoreNotInRange
     
         
     cursor.execute('''insert into daily_tracker (date , question_id , score , active) values (%s , %s , %s , %s )''' , (dia,id , score , value))

     return score
     
     



def enter_daily_data(conn , dia):
     cursor=conn.cursor()
     dih_lih=query_questions(conn)

     results={}

     try:
          for  layer , items in dih_lih.items():
               
               
               
                         
               results[layer]=0.0
               for dih in items:

                    checker = False
                    
                    while  not  checker :
                         
                         try:

                              score=enter_score_input(dih , cursor, dia)                         
                              
                              checker= True # if everything goes well
                              
                              results[layer]+=score
                    
                         except ScoreNotInRange:
                                   print('The score was higher than 1')
                                   
                         except ValueError:
                                   print("enter a number please")

                         
          total=sum(results.values())

          try:
               evidence = input('Enter evidence: ').strip()
               print()
               to_improve = input('Enter to impreve: ').strip()
          except EOFError:
               evidence = to_improve = ''
     
     except EOFError:
          print('you left the program')
          conn.rollback()
          return None


     
     confidence=results.get('internal_confidence', 0.0)
     courage=results.get('social_courage', 0.0)
     social=results.get('social_skills',0.0)
     romantic=results.get('romantic',0.0)
     business=results.get('competence',0.0)

     cursor.execute("select count(*) from daily_tracker  where date = %s and active = %s", (dia, True))
     total_questions = cursor.fetchone()[0]

     cursor.execute(''' insert into daily_result (date , total_score , internal_confidence_result , 
                        social_courage_result,  social_skills_result ,   romantic_result ,  business_result,
                          evidence , to_improve , total_questions ) values (%s , %s , %s , %s , %s , %s ,%s , %s ,%s , %s  )''' , (dia, total , confidence, courage , social , romantic, business , evidence , to_improve , total_questions))


     conn.commit()
     #========================================================================================================
     

def get_daily_result(conn , dia):
     cursor=conn.cursor()
     look_up={}
     cursor.execute(''' select date , total_score , internal_confidence_result , social_courage_result , social_skills_result , romantic_result , business_result ,  evidence , to_improve , total_questions from daily_result where date = %s ''', (dia,) )
     lista=cursor.fetchall()
     for dia , total , confidence , courage , social , romantic , business  , evidence , to_improve , total_questions in lista:
          look_up['date']=dia
          look_up['total_score']=total
          look_up['total_questions']=total_questions
          
          look_up['layers']={
               'internal confidence' : round(confidence, 2),
               'social courage' : round(courage,2) ,
               'social skills' : round(social,2),
               'romantic' : round(romantic,2),
               'business' : round(business , 2 )
               }  
            
          look_up['evidence']=evidence
          look_up['to_improve']=to_improve
     
     return look_up


          

def main():


     conn=initialize_connection()
     cursor=conn.cursor()
    
     opt=int(input('1) go to meu 2) add questions to db 3) see daily performance: ' ))
     if opt ==1:
          print()
          opt=input("Enter date y/n ?: ").lower()
          
          if opt == 'y':
              dia=input("Enter date: ").strip()
              dia=datetime.strptime(dia, "%Y-%m-%d").date()

          else:
               dia=d.today()         
          
          enter_daily_data(conn , dia)
          result=get_daily_result(conn , dia)

          for key , value in result.items():
                    if key == 'layers':
                         
                         print(f'{key} :')
                         print()
                         
                         for layer , score in value.items():
                              print(f'   {layer} : {score}')
                    
                    else:
                         print(f'{key} : {value}')
     
     elif opt == 2:
         enter_question_in_db(conn)
         

     elif opt == 3:
         cursor.execute(''' select date , total_score from daily_result ''')
         data=cursor.fetchall()

         for dia ,  number in data:
              print(f'{dia} == {number}')

     

    
if __name__ == "__main__":
    main()    
