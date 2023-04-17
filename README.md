Project Pacman

Python 3.11.1

pygame==2.2.0

Запуск:

git clone git@github.com:VasVol/project_pacman.git

cd project_pacman

git checkout dev

python3 main.py

Если ошибка из-за звука mixer, выполнить эти две строчки:

sudo apt-get install libsdl1.2-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev

sudo sdl-config --cflags --libs
