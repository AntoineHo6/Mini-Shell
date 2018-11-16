#! /usr/bin/python3

"""
Un mini shell qui peut executer des processus

Auteur: Antoine Ho
Date: 2018/11/15
"""

import os
import sys
import signal

# Global Variables
shellInv = "{}$?>".format(os.getenv("USER"))
processList = {}

def main():
    shellCommande = {"list": list, "tuer": tuer, "quitter": quitter}
    signal.signal(signal.SIGCHLD, deadChld)

    while True:
        entrer = input(shellInv)
        commande = entrer.lower().strip().split(" ")

        if commande[0] in shellCommande:
            if commande[0] == "tuer":
                shellCommande[commande[0]](commande[1])
            else:
                shellCommande[commande[0]]()

        elif len(commande[0]) > 0:
            tube = os.pipe()
            pid = os.fork()

            if pid == 0:
                os.close(tube[0])
                os.dup2(tube[1], 2)
                startChldPrcs(commande)
            elif pid > 0:
                processList[pid] = [commande[0], tube]
            # else:


def list():
    """
    Liste les processus créés par le programme.

    :return None:
    """
    for pid in processList:
        print(pid, processList[pid][0])


def tuer(pid):
    """
    Essaye de tuer un processus identifier par son pid.

    :param pid: Le pid du processus a tuer.
    :return None:
    """
    try:
        pid = int(pid)
    except:
        pass

    if pid in processList:
        os.kill(pid, signal.SIGKILL)
    else:
        print("Processus n'est pas dans la liste de processus")


def quitter():
    """
    Quitte le programme. Si des processus créés par celui-ci sont toujours actifs, on demande a l'utilisateur
    s'il souhaite quitter.

    :return None:
    """
    reponse = "o"
    if len(processList) > 0:
        print("Il reste des processus actifs:")
        list()
        reponse = input("Voulez-vous les tuer (o/n)?: ")

    if reponse.lower() == "o":
        for pid in processList:
            tuer(pid)
        sys.exit(0)


def startChldPrcs(commande):
    """
    Executer la commande entrer,

    :param commande: commande entrer par l'utilisateur
    :return None:
    """
    print("\nProgramme {0} déclanché avec le pid {1}".format(commande[0], os.getpid()))
    print(shellInv, end='', flush=True)

    if len(commande) > 1:
        os.execvp(commande[0], commande[1:])
    else:
        # Une commandee sans argument a ete entrer
        os.execvp(commande[0], commande)


def deadChld(signalnum, frame):
    """
    Ecrit dans erreurs.txt le processus executés et ses erreurs s'il y en a.

    :param signalnum: pas utilisé
    :param status: Status du processus a sa mort
    :return None:
    """
    pid, status = os.wait()

    if status != 0:
        # processList[pid][1] est le tube du processus
        os.close(processList[pid][1][1])
        lecture = os.fdopen(processList[pid][1][0])
        file = open("erreurs.txt", 'a')

        separateur = "#" * 65 + "\n"
        file.write(separateur)
        file.write("{0}{1}".format(processList.get(pid)[0], "\n"))
        erreur = lecture.read()
        file.write(erreur)
        file.close()

    processList.pop(pid)

    print("\nLe processus {} est terminé".format(pid))
    print(shellInv, end='', flush=True)


if __name__ == "__main__":
    os.system("reset")
    main()