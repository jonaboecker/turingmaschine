# Turingmaschine
HTWG AIN team project TMZA with Barbara Staehle

## External Docs
- [Google Drive](https://drive.google.com/drive/folders/1JHxRtSFg7mk2hAvrhvDHg5vqaU5e4cNY)

## Flask Deployment
After every push or pull-request on main Branch to path raspberry/** a Docker image is generated via a workflow. You can Download the current Image in the Github Web-Interface as Artifact under the current Action-Run.

### Start Docker Container

Unzip the `.tar`-File on your local Device and import it with Docker

```bash
docker load < flask-app.tar
```

After Import Docker will confirm that the Image was loaded successfully e.g.
```
Loaded image: flask-app:latest
```

---

Now you can use the Image to start your Container

```bash
docker run -p 5000:5000 flask-app:latest
```

- **`-p 5000:5000`**: Forwards port `5000` of the container to port `5000` of your host.

After starting, the Flask app should be accessible at [http://localhost:5000](http://localhost:5000).

---
