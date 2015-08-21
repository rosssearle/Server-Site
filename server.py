from flask import Flask, render_template, request, redirect, url_for, Markup
from flask_mail import Mail, Message
import os, random
app = Flask(__name__)
app.config.from_object(__name__)
mail = Mail(app)
app.config.update(
	DEBUG=False,
	#EMAIL SETTINGS
	MAIL_SERVER='smtp.gmail.com',
        MAIL_PORT=587,
        MAIL_USE_SSL=False,
        MAIL_USE_TLS=True,
	MAIL_USERNAME = 'ross.minecraft@gmail.com',
	MAIL_PASSWORD = ''
	)
mail=Mail(app)
password = ""

def sendMail(who, text):
    msg = Message('SurvivalCraft',sender='ross.minecraft@gmail.com')
    msg.add_recipient(who)
    msg.body = text
    with app.app_context():
        mail.send(msg)

@app.route('/')
def home():
    return render_template('index.html')
@app.route('/Post/', methods=["POST", "GET"])
def p():
    if request.method == 'POST':
        input_list = []
        list = ["fn","ign","age","email","ts","why","about","offer","sone","stwo","sthree"]
        for i in list:
            input_list.append(str(request.form[i]))
        name = str(input_list[0].replace(" ", ""))
        while os.path.exists("Posts/" + str(name) + ".txt"):
            name = name + str(random.randint(1,100))
        with open("Posts/" + str(name) + ".txt", "w") as file:
            for i in input_list:
                file.write(str(i) + "\n")
                
        error = None
        if not error:
            sendMail(request.form['email'],"Thank you for applying, " + request.form['fn'] + ".\nA admin will review your application shortly")
        return render_template("posted.html", error=error)
    else:
        return redirect(url_for("home"))
@app.route('/View/')
def view():
    post = ""
    files = os.listdir("Posts/")
    if not files:
        post = None
    else:
        for file in files:
            post = post + Markup("<button onclick='gotourl(\"/View/" + file.replace(".txt", "") + "\")'>" + file.replace(".txt","") + "</button><br />")
    return render_template("view.html", post=post)
@app.route("/View/<file>")
def ViewFile(file):
    if "[Accepted]" in file: error = "[Accepted]"
    elif "[Denied]" in file: error = "[Denied]"
    else: error = None
    list = []
    with open("Posts/" + file + ".txt", "r+") as ofile:
        for line in ofile:
            list.append(line)
    return render_template("ViewFile.html", name=list[0].replace("\n",""), ign=list[1], age=list[2], ts=list[4], why=list[5], about=list[6], offer=list[7], sone=list[8], stwo=list[9],sthree=list[10], error=error, namens=file)
@app.route("/View/<file>/Deny", methods=["GET", "POST"])
def deny(file):
    error = None
    list = []
    if request.method == 'POST':
        if request.form['password'] == password:
            with open("Posts/" + file + ".txt", "r+") as openfile:
                for line in openfile:
                    list.append(line)
            reason = request.form['reason']
            sendMail(list[3].replace("\n", ""), "I am sorry to say, " + list[0] + "But you application for staff has been denied. You may re-apply anytime. \n The reason it was denied is because: " + reason)
            os.rename("Posts/" + file + ".txt", "Posts/[Denied]" + file + ".txt")
            return redirect("/View")
        else:
            error = "Wrong Password"
    return render_template("Deny.html", error=error)

@app.route("/View/<file>/Accept", methods=["GET", "POST"])
def accept(file):
    error = None
    list = []
    if request.method == 'POST':
        if request.form['password'] == password:
            with open("Posts/" + file + ".txt", "r+") as openfile:
                for line in openfile:
                    list.append(line)
            sendMail(list[3].replace("\n", ""), "I am happy to say, " + list[0] + "you're application for staff has been accepted.")
            os.rename("Posts/" + file + ".txt", "Posts/[Accepted]" + file + ".txt") 
            return redirect("/View")
        else:
            error = "Wrong Password"
    return render_template("Accept.html", error=error)
@app.errorhandler(404)
def page_not_found(e):
    return redirect("/")
@app.route("/Request/", methods=['GET', 'POST'])
def Request():
    if request.method != "POST":
        return redirect("/#Request")
    input_list = []
    list = ["fn","ign","age","email","what","b"]
    for i in list:
        input_list.append(str(request.form[i]))
    name = str(input_list[5].replace(" ", ""))
    while os.path.exists("Requests/" + str(name) + ".txt"):
        name = name + str(random.randint(1,100))
    open("Requests/" + str(name) + "_Votes.txt", "w")
    with open("Requests/" + str(name) + ".txt", "w") as file:
        for i in input_list:
            file.write(str(i) + "\n")
            
    error = None
    if not error:
        sendMail(request.form['email'],"Thank you for making a Request, " + request.form['fn'] + ".\nif it gets enough votes it will be added")
    return render_template("reqeust.html", error=error)
@app.route("/Requests/")
def viewRequests():
    error = None
    errort = None
    errord = None
    if request.args.get('e', 'fail') != "fail":
        error = request.args.get('e', '')
    elif request.args.get('et', 'fail') != "fail":
        errort = request.args.get('et', '')
    elif request.args.get('ed', 'fail') != "fail":
        errord = request.args.get('ed', '')
    else:
        error = None
        errort = None
        errord = None
    post = ""
    files = os.listdir("Requests/")
    if not files:
        post = None
    else:
        for file in files:
            if "_Votes" not in file:
                votes = 0
                with open("Requests/" + file.replace(".txt", "").replace("[Denied]", "") + "_Votes.txt", "r+") as openfile:
                    for line in openfile:
                        votes = votes + 1
                post = post + Markup("<button onclick='gotourl(\"/Requests/" + file.replace(".txt", "") + "\")'>" + file.replace(".txt","") + " [Votes: " + str(votes) + "]</button><br />")
    return render_template("viewRequests.html", post=post, errort=errort, error=error, errord=errord)

@app.route("/Requests/<file>")
def viewRequestsFile(file):
    error = None
    errorInfo = None
    list = []
    with open("Requests/" + file + ".txt", "r+") as ofile:
        for line in ofile:
            list.append(line)
    if "[Denied]" in file:
        error = "[Denied]" 
        errorInfo = str(list[6])
    votes = 0
    with open("Requests/" + file.replace(".txt", "").replace("[Denied]", "") + "_Votes.txt", "r+") as openfile:
        for line in openfile:
            votes = votes + 1
    namevote = file + " [Votes: " + str(votes) + "]"
    return render_template("ViewRequestsFiles.html", name=list[0].replace("\n",""), ign=list[1], age=list[2], what=list[4], b=list[5], error=error, errorInfo=errorInfo, namens=file, namevote=namevote)

@app.route("/Requests/<file>/Deny", methods=["GET", "POST"])
def denyRequests(file):
    error = None
    list = []
    if request.method == 'POST':
        if request.form['password'] == password:
            with open("Requests/" + file + ".txt", "r+") as openfile:
                for line in openfile:
                    list.append(line)
            reason = request.form['reason']
            sendMail(list[3].replace("\n", ""), "I am sorry to say, " + list[0] + "But you Request is denied. The Reason for this is: \n" + reason)
            with open("Requests/" + file + ".txt", "a") as openfile:
                openfile.write(reason)
            os.rename("Requests/" + file + ".txt", "Requests/[Denied]" + file + ".txt")
            return redirect("/Requests")
        else:
            error = "Wrong Password"
    return render_template("rDeny.html", error=error)
@app.route("/Requests/<file>/Vote", methods=["GET", "POST"])
def Vote(file):
    if "[Denied]" in file:
        return redirect("/Requests/?ed=" + file)
    with open("Requests/" + file + "_Votes.txt", "r") as openfile:
        for line in openfile:
            if request.environ['REMOTE_ADDR'] in line:
                return redirect("/Requests/?et=" + file)
    with open("Requests/" + file + "_Votes.txt", "a") as openfile:
        openfile.write(str(request.environ['REMOTE_ADDR']) + "\n")
        return redirect("/Requests/?e=" + file)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=False)
