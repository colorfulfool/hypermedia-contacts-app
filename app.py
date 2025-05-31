from flask import Flask, redirect, request, render_template, flash
from contact import Contact

app = Flask(__name__)

app.debug = True
app.secret_key = "SEC"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEVELOPMENT"] = True

Contact.create_table()

@app.route("/")
def index():
    return redirect("/contacts")

@app.route("/contacts")
def contacts():
    search = request.args.get("q")
    if search is not None:
        contacts_set = Contact.search(search)
    else:
        contacts_set = Contact.all()
    return render_template("index.html", contacts=contacts_set)

@app.route("/contacts/new", methods=['GET'])
def contacts_new_get():
    return render_template("new.html", contact=Contact())

@app.route("/contacts/new", methods=['POST'])
def contacts_new_post():
    c = Contact(
      None,
      request.form['first_name'],
      request.form['last_name'],
      request.form['phone'],
      request.form['email'])
    if c.save():
        flash("Created New Contact!")
        return redirect("/contacts")
    else:
        return render_template("new.html", contact=c)

@app.route("/contacts/<contact_id>")
def contacts_view(contact_id=0): 
    contact = Contact.find(contact_id) 
    return render_template("show.html", contact=contact) 

@app.route("/contacts/<contact_id>/edit", methods=['GET'])
def contacts_edit_get(contact_id=0): 
    contact = Contact.find(contact_id) 
    return render_template("edit.html", contact=contact) 

@app.route("/contacts/<contact_id>/edit", methods=['POST'])
def contacts_edit_post(contact_id=0):
    c = Contact(
      contact_id,
      request.form['first_name'],
      request.form['last_name'],
      request.form['phone'],
      request.form['email'])
    if c.save():
        flash("Updated Contact!")
        return redirect("/contacts")
    else:
        return render_template("edit.html", contact=c)

@app.route("/contacts/<contact_id>/delete", methods=['POST'])
def contacts_delete(contact_id=0):
    contact = Contact.find(contact_id)
    if contact.delete():
        flash("Deleted Contact!")
        return redirect("/contacts")
    else:
        flash("Couldn't delete")
        return render_template("edit.html", contact=contact)
