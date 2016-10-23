#include <sys/types.h> // } for
#include <sys/stat.h> //  } umask()
#include <unistd.h> // fork, sleep, ...
#include <stdlib.h>
#include <string>
#include <ctime>
#include <fstream>

using namespace std;

const string command = "python ../src/fttg.py";

void logger(const string& text) {
    ofstream log("../log.txt", ios::app);
    time_t now = time(0);
    string dt = ctime(&now);
    log << dt << " " << text << endl;
    log.close();
}

void process() {
    // Create a fork which will continue to run main loop
    if (pid_t pid = fork()) {
        // Launch command in parent process and exit
        if (pid > 0) {
            logger("Launching python script");
            execl("/bin/sh", "sh", "-c", command.c_str(), (char *) 0);
            exit(0);
        }
        else if (pid < 0) {
            logger("Failed to launch python script");
        }
    }
}

int daemonize() {
    // Fork the process and have the parent exit. If the process was started
    // from a shell, this returns control to the user. Forking a new process is
    // also a prerequisite for the subsequent call to setsid().
    if (pid_t pid = fork())
    {
        if (pid > 0)
        {
            // We're in the parent process and need to exit.
            //
            // When the exit() function is used, the program terminates without
            // invoking local variables' destructors. Only global variables are
            // destroyed.
            exit(0);
        }
        else
        {
            logger("First fork failed");
            return 1;
        }
    }

    // The file mode creation mask is also inherited from the parent process.
    // We don't want to restrict the permissions on files created by the
    // daemon, so the mask is cleared.
    logger("Changing file mask");
    umask(0);

    // Make the process a new session leader. This detaches it from the
    // terminal.
    pid_t sid = setsid();
    logger("Creating new signature for the fork, PID " + to_string(sid));
    
    if (sid < 0) {
        logger("Signature creation failed");
        exit(EXIT_FAILURE); 
    }

    /*  -- Not using this because python script should be in the same
    directory as the daemon --
    
    // A process inherits its working directory from its parent. This could be
    // on a mounted filesystem, which means that the running daemon would
    // prevent this filesystem from being unmounted. Changing to the root
    // directory avoids this problem.
    // If we can't find the directory we exit with failure.
    logger("Changing directory");
    
    if ((chdir("/")) < 0) {
        logger("Failed to change directory");
        exit(EXIT_FAILURE); 
    }
    */

    // A second fork ensures the process cannot acquire a controlling terminal.
    if (pid_t pid = fork())
    {
        if (pid > 0)
        {
            exit(0);
        }
        else
        {
            logger("Second fork failed");
            return 1;
        }
    }

    // Close the standard streams. This decouples the daemon from the terminal
    // that started it.
    close(STDIN_FILENO);
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
    
    return 0;
}

int main() {
    logger("Starting daemon");
    
    if ( daemonize() == 0 ) {
        // Main process
        while(true) {
            process();
            logger("Sleeping");
            sleep(60);
        }
    }
    
    logger("Exiting");
}
