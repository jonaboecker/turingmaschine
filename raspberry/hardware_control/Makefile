# Compiler & Flags
CXX = g++
CXXFLAGS = -Wall -O2
LDFLAGS = -lwiringPi

# Dateien
TARGET = color_sensor
SRC = color_sensor.cpp

# Regel zum Kompilieren des Programms
$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC) $(LDFLAGS)

# `make clean` löscht die ausführbare Datei
clean:
	rm -f $(TARGET)