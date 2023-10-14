import ipfs_client
from util import Timer

# QmYZS1Xe57CqpjkqSSdJu62hs62dF22xDhCddELmA2kHE4
# QmZUGJSngUEJ4BdYHeeyxXPwHWizAoxhmRjy6dqNo7h8Zt
# QmYVra6BXcpH6eaLXwnH5TgrzxKfcACW3pWAE299rjiRxv
# QmPzyRzJT4Ay8w2vMjt7jZ782k9dUjW9tu8dtoZtmAiWzA
# QmfGE3tr4ctW3PzpaJjNNjA4fXEuf7x522wfJcSfsPwVAK
# QmVSE9cCZVuinGdMuKekYsDHNCGYVjhUXcc8VkyF7zkC35
# QmVWWqFW2JzJ85TV71E99EK5SxB3JDri9nvDpLEMAHFD7s
# QmaDGHx7VXrRZB9JuVsJW4FS89nkEEBKEr5EpGBTw1mmmE
# QmVLfE9Ldn3Snsa2zRJ87gX2xrrGZzo9e42U7TziCWisdZ
# Qmf9rhRbfuY2VrNUhPzmWt26xdZV1S29VQAGqt9HrrRmia
def g8():
    id = 'Qmf9rhRbfuY2VrNUhPzmWt26xdZV1S29VQAGqt9HrrRmia'

    iterations = 10
    for i in range(iterations):
        with Timer('phr_download', id):
            print(ipfs_client.download(id))


if __name__ == '__main__':
    g8()