from flask import Flask, redirect, request, render_template, flash
from contact import Contact

app = Flask(__name__)

app.debug = True
app.secret_key = "SEC"
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["DEVELOPMENT"] = True

Contact.create_table()
Contact.seed()

@app.route("/")
def index():
    return redirect("/contacts")

@app.route("/contacts")
def contacts():
    search = request.args.get("q")
    page = int(request.args.get("page", 1))
    if search is not None:
        contacts_set = Contact.search(search)
        if request.headers.get("HX-Trigger") == "search":
            return render_template("rows.html", contacts=contacts_set)
    else:
        contacts_set = Contact.all(page)
    return render_template("index.html", contacts=contacts_set, page=page)

@app.route("/contacts/count")
def contacts_count():
    count = Contact.count()
    return f"{count} total Contacts"

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

@app.route("/contacts/<contact_id>", methods=['DELETE'])
def contacts_delete(contact_id=0):
    contact = Contact.find(contact_id)
    if contact.delete():
        if request.headers.get("HX-Request"):
            return ''
        flash("Deleted Contact!")
        return redirect("/contacts", 303)
    else:
        flash("Couldn't delete")
        return render_template("edit.html", contact=contact)

@app.route("/contacts", methods=['DELETE'])
def contacts_delete_many():
    contact_ids = [int(id) for id in request.form.getlist("selected_contact_ids")]
    page = int(request.form.get("page"))
    for contact_id in contact_ids:
        contact = Contact.find(contact_id)
        contact.delete()
    flash("Deleted Contacts!")
    contacts_set = Contact.all(page)
    return render_template("index.html", contacts=contacts_set, page=page)

@app.route("/contacts/<contact_id>/email", methods=["GET"])
def contacts_email_get(contact_id=0):
    c = Contact.find(contact_id) 
    c.email = request.args.get('email') 
    c.validate() 
    return c.errors.get('email') or "" 
