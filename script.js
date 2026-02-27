class Quarter {
	constructor(position) {
  	this.position = position;
  }

  flash(position, timer, callback) {
    document.getElementById(position).style.opacity = 0.5;
    play(position);
    setTimeout(() => {
      document.getElementById(position).style.opacity = 1;
       if (callback) callback();
    }, timer);

  }
};

class Game {
  constructor() {
    this.quarters = [
      new Quarter('topleft'),
      new Quarter('topright'),
      new Quarter('bottomleft'),
      new Quarter('bottomright')
    ];
    this.sequence = [];
    //this.timer = 1000;
    this.canGuess = false;
    this.seqPosition = 0;
    this.highScore = 0;
    this.strictMode = false;
    this.power = false;
  }

  gameOver() {
    alert('you lost');
    this.newStart();
  }

  guess(guessedSquare, index) {

    //if Game.power is false i.e. game is turned off, then no guesses can be made

    if (this.power === false) return;

    //Game.canGuess is a property that toggles between two states, one where we have control and can make a guess and
    //another were the computer is in control i.e. playing the sequence to be guessed

    if (!this.canGuess) return;

    guessedSquare.flash(this.quarters[index].position, 250, () => {

      //guessing logic

      if (guessedSquare.position === this.sequence[this.seqPosition].position) {

        //correctly guessed the current position in Game.sequence i.e. the random sequence generated so far.

        if (this.seqPosition === (this.sequence.length - 1)) {

          //if the item we correctly guessed was the last item in the sequence we set a new high score and move onto
          //the next round

          if (this.sequence.length > this.highScore) {

            //set new high score

            this.highScore = this.sequence.length;
          }

          //move on to the next round i.e. add new item to sequence and repeat guessing process

          this.newRound();

        } else {

          //increment Game.seqPosition if item we correctly guessed is not the last item in the Game.sequence array.

          this.seqPosition++;
        }

      } else {

        //else branch related to correct guess above. Here we have guessed incorrectly and the game will end and prevent
        //any further guesses by setting Game.canGuess to false

        if (this.strictMode === true) {

          this.gameOver();

          this.canGuess = false;

        } else {

          this.replayRound(index);

        }
      }
    });
  }

  playSequence(index) {
    let self = this;
    let ind = index || 0;

    self.sequence[ind].flash(self.sequence[ind].position, 250, function() {
      if (self.sequence[ind + 1]) {
        setTimeout(() => {
          self.playSequence(ind + 1);
        }, 250);
      } else {
        self.canGuess = true;
      }
    });
  }

  replayRound() {
    alert('WRONG CHOICE');
    let self = this;
    setTimeout(function() {
      document.getElementById('score').innerHTML = '<div id = "inner-score-display"><p id = "current-score"> ' + (self.highScore + 1) + '</p></div>';
      self.canGuess = false;
      self.seqPosition = 0;
      self.playSequence();
    }, 250);
  }

  newRound() {
    let self = this;
    if (self.highScore === 20) {
      alert('YOU WIN');
      this.newStart();
    } else {
      setTimeout(function() {
        document.getElementById('score').innerHTML = '<div id = "inner-score-display"><p id = "current-score"> ' + (self.highScore + 1) + '</p></div>';
        self.canGuess = false;
        self.seqPosition = 0;
        self.sequence.push(self.quarters[Math.floor(Math.random() * 4)]);
        self.playSequence();
      }, 250);
    }
  }

  newStart() {
    if (this.power === false) return;
    this.sequence = [];
    this.highScore = 0;
    this.newRound();
  }
};

let play = (position) => {

  let whichSound = position + 'audio';
  document.getElementById(whichSound).play();
}

document.getElementById('start').onclick = () => {
  simonGame.newStart();
}

document.getElementById('topleft').onclick = () => {
  simonGame.guess(simonGame.quarters[0], 0);
}

document.getElementById('topright').onclick = () => {
  simonGame.guess(simonGame.quarters[1], 1);
}

document.getElementById('bottomleft').onclick = () => {
  simonGame.guess(simonGame.quarters[2], 2);
}

document.getElementById('bottomright').onclick = () => {
  simonGame.guess(simonGame.quarters[3], 3);
}

document.getElementById('power').onclick = () => {
  simonGame.guess(simonGame.quarters[3], 3);
}

document.getElementById('mode').onclick = () => {
  if (simonGame.power === false) return;
  if (simonGame.strictMode === true) {
    simonGame.strictMode = false;
    document.getElementById('mode-state').innerHTML = "<div id = 'inner-mode-state'></div>";
  } else {
    simonGame.strictMode = true;
    document.getElementById('mode-state').innerHTML = "<div id = 'inner-mode-state' class = 'round-button-inner-mode-state'></div>";
  }
}

document.getElementById('power').onclick = () => {
  if (simonGame.power === true) {
    simonGame.power = false;
    document.getElementById('score').innerHTML = '<div id = "inner-score-display"><p id = "current-score"></p></div>';
    document.getElementById('power').innerHTML = '<p id = "power-off">OFF</p><div id = "switch-left"></div><p id = "power-on">ON</p>';
    document.getElementById('mode-state').innerHTML = "<div id = 'inner-mode-state'></div>";
  } else {
    simonGame.power = true;
    document.getElementById('score').innerHTML = '<div id = "inner-score-display"><p id = "current-score">00</p></div>';
    document.getElementById('power').innerHTML = '<p id = "power-off">OFF</p><div id = "switch-right"></div><p id = "power-on">ON</p>';
  }
}

let simonGame = new Game();
