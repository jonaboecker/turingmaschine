[![License](https://img.shields.io/github/license/jonaboecker/turingmaschine?color=green)](https://cdn130.picsart.com/272563229032201.jpg?r1024x1024)
![RepoSize](https://img.shields.io/github/repo-size/jonaboecker/turingmaschine)
![Lines of Code](https://tokei.rs/b1/github/jonaboecker/turingmaschine)

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

## Contributors
| [Jona Böcker](https://github.com/jonaboecker)  | [Tobias Stöhr](https://github.com/TobiasReyEye)  | [Julian Rapp](https://github.com/Julz124)  |  [Lara Geyer](https://github.com/lara00) | [Dennis Schulze](https://github.com/l0n1y)  |
|---|---|---|---|---|
| ![image](https://github-readme-streak-stats.herokuapp.com/?user=jonaboecker) | ![image](https://github-readme-streak-stats.herokuapp.com/?user=TobiasReyEye)  | ![image](https://github-readme-streak-stats.herokuapp.com/?user=Julz124) | ![image](https://github-readme-streak-stats.herokuapp.com/?user=lara00)  |![image](https://github-readme-streak-stats.herokuapp.com/?user=l0n1y) |

