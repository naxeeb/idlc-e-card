import os
import json
from flask import Flask, render_template, request, redirect, url_for, send_file
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

# Configuration variables
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')
app.config['CONFIG_FILE'] = 'config.json'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def save_config(data):
    with open(app.config['CONFIG_FILE'], 'w') as f:
        json.dump(data, f)

def load_config():
    if os.path.exists(app.config['CONFIG_FILE']):
        with open(app.config['CONFIG_FILE'], 'r') as f:
            return json.load(f)
    # Return default settings if config file doesn’t exist
    return {
        "template_image": "",
        "name": {
            "x": 50,
            "y": 50,
            "font": "arial.ttf",  # You can change to a full path if needed
            "size": 40,
            "color": "#000000",
            "alignment": "center"
        },
        "designation": {
            "x": 50,
            "y": 120,
            "font": "arial.ttf",
            "size": 30,
            "color": "#000000",
            "alignment": "center"
        }
    }

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    config = load_config()
    if request.method == 'POST':
        # --- Process file upload ---
        if 'template_image' in request.files:
            file = request.files['template_image']
            if file and file.filename != "":
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                config['template_image'] = filepath

        # --- Update text positions and styling from form fields ---
        try:
            config['name']['x'] = int(request.form.get('name_x', config['name']['x']))
            config['name']['y'] = int(request.form.get('name_y', config['name']['y']))
            config['name']['color'] = request.form.get('name_color', config['name']['color'])
            config['name']['size'] = int(request.form.get('name_size', config['name']['size']))
            config['name']['font'] = request.form.get('name_font', config['name']['font'])
            config['name']['alignment'] = request.form.get('name_alignment', config['name']['alignment'])

            config['designation']['x'] = int(request.form.get('designation_x', config['designation']['x']))
            config['designation']['y'] = int(request.form.get('designation_y', config['designation']['y']))
            config['designation']['color'] = request.form.get('designation_color', config['designation']['color'])
            config['designation']['size'] = int(request.form.get('designation_size', config['designation']['size']))
            config['designation']['font'] = request.form.get('designation_font', config['designation']['font'])
            config['designation']['alignment'] = request.form.get('designation_alignment', config['designation']['alignment'])
        except Exception as e:
            print("Error reading form fields:", e)

        save_config(config)
        return redirect(url_for('admin'))

    return render_template('admin.html', config=config)

@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        name = request.form.get('name', '')
        designation_text = request.form.get('designation', '')
        return redirect(url_for('generate', name=name, designation=designation_text))
    return render_template('user.html')

@app.route('/generate')
def generate():
    # Get text values from query string
    name_text = request.args.get('name', '')
    designation_text = request.args.get('designation', '')
    
    config = load_config()
    template_image_path = config.get('template_image')
    if not template_image_path or not os.path.exists(template_image_path):
        return "Template image not found. Please set it in the admin panel.", 404

    # Open the template image
    image = Image.open(template_image_path)
    draw = ImageDraw.Draw(image)

    # Load fonts – note: You must have these .ttf files accessible
    try:
        name_font = ImageFont.truetype(config['name']['font'], config['name']['size'])
    except IOError:
        name_font = ImageFont.load_default()
    try:
        designation_font = ImageFont.truetype(config['designation']['font'], config['designation']['size'])
    except IOError:
        designation_font = ImageFont.load_default()

    # Draw the texts at the stored positions (you can add alignment logic here if needed)
    draw.text((config['name']['x'], config['name']['y']), name_text, font=name_font, fill=config['name']['color'])
    draw.text((config['designation']['x'], config['designation']['y']), designation_text, font=designation_font, fill=config['designation']['color'])

    # Save and serve the output image
    output_path = os.path.join(app.config['UPLOAD_FOLDER'], 'output.png')
    image.save(output_path)
    return send_file(output_path, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
