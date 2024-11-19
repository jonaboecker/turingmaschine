# UI for Turing Machine on Raspberry PI
This Python Flask Applikation manages the robot on the Turing Machine and provides a user-friendly interface.

## Development Environment

### Setting up Python:

Install: python3.12 python3.12-dev python3.12-venv

Setting up an isolated environment:
```
python3.12 -m venv venv
```

This sets up everything in the `venv` directory.
Activate it using:
```
source venv/bin/activate
```
Deactivate using
```
deactivate
```

Now you can install packages without affecting other projects or your
global Python installation:
```
pip install -r requirements.txt
```

## Tailwind CSS
Tailwind CSS is a utility-first CSS framework for rapidly building custom user interfaces.
Further information can be found at [Tailwind CSS](https://tailwindcss.com/).
### Installation
To install Tailwind CSS, use the following command:
```bash
npm install tailwindcss
```
### Configuration
Tailwind config file (`tailwind.config.js`) is used to customize the default settings of Tailwind CSS.
### Generate CSS
To generate CSS file from Tailwind CSS, use the following command:
```bash
npx tailwindcss -i ./static/tailwind/input.css -o ./static/tailwind/tailwind_style.css --watch
```
css code will generate in `/static/tailwind/tailwind_style.css` file.
### Usage
To use Tailwind CSS in your project, include the CSS file in your HTML file:
```html
<link rel="stylesheet" href="/static/tailwind/tailwind_style.css">
```
