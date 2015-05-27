# Modified version from the last example of below page
# http://mrbook.org/blog/tutorials/make/

CC=gcc
CFLAGS=-c -O0
LDFLAGS=-lm -lpthread
SOURCES=mp_task_sim.c
OBJECTS=$(SOURCES:.c=.o)
EXECUTABLE=$(SOURCES:.c=)

all: $(SOURCES) $(EXECUTABLE)

$(EXECUTABLE): $(OBJECTS) 
	$(CC) $(LDFLAGS) $(OBJECTS) -o $@

.c.o:
	$(CC) $(CFLAGS) $< -o $@

clean:
	rm -rf $(OBJECTS) $(EXECUTABLE)

tests: $(EXECUTABLE)
	./$(EXECUTABLE) 5 8
