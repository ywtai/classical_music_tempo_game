from flask import Flask, render_template, request
import sqlite3
from collections import defaultdict
import os

app = Flask(__name__)
con = sqlite3.connect(os.path.join(os.path.dirname(os.path.realpath(__file__)),'static/music_game.db'), check_same_thread=False)
cur = con.cursor()
arrow_timing = []
vid_duration = 0
music_title = ""
point = 0
buffer = 0.02

def check_timing_sql():
    sql = 'select * from turkish_march_easy'
    cur.execute(sql)
    content = cur.fetchall()
    
    if len(content) == 0:
        txt = os.path.join(os.path.dirname(os.path.realpath(__file__)),'static/turkish_march_easy_timing.txt')
        f = open(txt, 'r')
        timings = f.readlines()
        i = 0
        for timing in timings:
            start = str(float(timing.split(' ')[0]))
            end = str(float(timing.split(' ')[1]))
            arrow = '\'' + timing.split(' ')[-1].split('\n')[0] + '\''
            sql = "insert into turkish_march_easy values(" + str(i) + ", " + start + ", " + end + ", " + arrow + ", 'null')"
            cur.execute(sql)
            i += 1

        f.close()

    sql = 'select * from turkish_march_normal'
    cur.execute(sql)
    content = cur.fetchall()
    
    if len(content) == 0:
        txt = os.path.join(os.path.dirname(os.path.realpath(__file__)),'static/turkish_march_normal_timing.txt')
        f = open(txt, 'r')
        timings = f.readlines()
        i = 0
        for timing in timings:
            start = str(float(timing.split(' ')[0]))
            end = str(float(timing.split(' ')[1]))
            arrow = '\'' + timing.split(' ')[-1].split('\n')[0] + '\''
            sql = "insert into turkish_march_normal values(" + str(i) + ", " + start + ", " + end + ", " + arrow + ", 'null')"
            cur.execute(sql)
            i += 1

        f.close()

def init_con():
    #create music game timing and ranks table if not exists
    sql = """CREATE TABLE IF NOT EXISTS turkish_march_easy('id' integer,
                                                'start_time' float,
                                                'end_time' float,
                                                'arrow' text,
                                                'success' text
                                                );"""
    cur.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS turkish_march_easy_rank('name' text,
                                                        'score' integer
                                                        );"""
    cur.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS turkish_march_normal('id' integer,
                                                'start_time' float,
                                                'end_time' float,
                                                'arrow' text,
                                                'success' text
                                                );"""
    cur.execute(sql)

    sql = """CREATE TABLE IF NOT EXISTS turkish_march_normal_rank('name' text,
                                                        'score' integer
                                                        );"""
    cur.execute(sql)

    #insert timing into tables if not exist
    check_timing_sql()

def rank_calculate(rank_name):
    rank_list = get_rank(rank_name)
    print(len(rank_list))

    score_list = []
    sorted_rank = defaultdict(list)

    for i in range(len(rank_list)):
        score_list.append(rank_list[i][1])

    sorted_score = sorted(score_list, reverse=True)
    sorted_rank_index = sorted(range(len(score_list)), key=lambda k: score_list[k], reverse=True)

    if len(score_list) < 3:
        for i in range(3-len(score_list)):
            sorted_rank['rank'+str(i+1+len(score_list))].extend(['- ', '-'])

        for i in range(len(score_list)):
            index = sorted_rank_index[i]
            sorted_rank['rank'+str(i+1)].append(rank_list[index][0])
            sorted_rank['rank'+str(i+1)].append(rank_list[index][1])

    else:
        for i in range(3):
            index = sorted_rank_index[i]
            sorted_rank['rank'+str(i+1)].append(rank_list[index][0])
            sorted_rank['rank'+str(i+1)].append(rank_list[index][1])
        
    return sorted_rank

def get_timing():
    sql = 'select id, start_time, end_time, arrow from ' + music_title + "_" + difficulty
    cur.execute(sql)
    content = cur.fetchall()
    return content

def get_success_status():
    sql = 'select id, success from ' + music_title + "_" + difficulty
    cur.execute(sql)
    content = cur.fetchall()

    return content 

def get_rank(rank_name):
    sql = 'select * from ' + rank_name + '_rank'
    cur.execute(sql)
    content = cur.fetchall()
    
    return content 

def check_arrow_timing(now_arrow, time_stamp):
    global point
    status = ""
    intime = "false"

    if time_stamp is not '0' and float(time_stamp) < vid_duration:
        status = "fail"
        for i in range(len(arrow_timing)):
            start = arrow_timing[i][1]
            end = arrow_timing[i][2]
            arrow = arrow_timing[i][3]

            if float(time_stamp) >= start - buffer and float(time_stamp) <= end + buffer:
                success = get_success_status()[i][1]
                intime = "true"
                if now_arrow == arrow:
                    if success == 'null':
                        status = "success"
                        sql = "update " + music_title + "_" + difficulty + " set success='success' where id=" +  str(i)
                        cur.execute(sql)
                        point += 5

                    elif success == 'success':
                        status = "success"
                
                    break

                else:
                    status = "fail"
                    if success != 'fail':
                        sql = "update " + music_title + "_" + difficulty + " set success='fail' where id=" +  str(i)
                        cur.execute(sql)
                        
                    point -= 5
                    break
            
        if intime == "false":
            point -= 5

    return {'point': point, 'status': status}

@app.route('/')
def index():
    global difficulty
    difficulty = ""
    
    init_con()
    return render_template("index.html")

@app.route('/turkish_march_easy', methods=['GET'])
def turkish_march_easy():
    global arrow_timing
    global music_title
    global difficulty, point
    point = 0
    music_title = "turkish_march"
    difficulty = "easy"
    arrow_timing = get_timing()
    sql = "update turkish_march_easy set success = 'null'"
    cur.execute(sql)

    return render_template("turkish_march_easy.html")

@app.route('/turkish_march_normal')
def turkish_march_normal():
    global arrow_timing
    global music_title
    global difficulty, point
    point = 0
    music_title = "turkish_march"
    difficulty = "normal"
    arrow_timing = get_timing()
    sql = "update turkish_march_normal set success = 'null'"
    cur.execute(sql)
    return render_template("turkish_march_normal.html")

@app.route('/rank')
def rank():
    turkish_march_easy_rank = rank_calculate('turkish_march_easy')
    turkish_march_normal_rank = rank_calculate('turkish_march_normal')
        
    return render_template("rank.html", turkish_march_easy_rank=turkish_march_easy_rank, turkish_march_normal_rank=turkish_march_normal_rank)

@app.route('/video_time', methods=['GET'])
def video_time():
    global vid_duration
    vid_duration = int(float(request.args.get('vid_duration')))
    return str(vid_duration)

@app.route('/keyboard_status_get', methods=['GET'])
def keyboard_status_get():
    time_stamp = request.args.get('time_stamp')
    insert_arrow = request.args.get('jsdata')
   
    if time_stamp is not '0' and float(time_stamp) < vid_duration:
        return check_arrow_timing(insert_arrow, time_stamp)

    return "error"

@app.route('/submit_score', methods=['GET'])
def submit_score():
    score = request.args.get('point')
    player_name = request.args.get('player_name')

    player_name = "\'" + player_name + "\'"
    sql = "insert into " + music_title + "_" + difficulty + "_rank values(" + player_name + ", " + str(score) + ")"
    cur.execute(sql)

    return score

@app.route('/get_game_timing', methods=['GET'])
def get_game_timing():
    game_timing = defaultdict(list)

    for i, value in enumerate(arrow_timing):
        game_timing[i].append(value[2])
        game_timing[i].append(value[3])
   
    return game_timing
        
if __name__ == "__main__":
    app.run(debug=True)