class SnakeGame {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.gridSize = 20;
        this.tileCount = this.canvas.width / this.gridSize;

        // Game state
        this.snake = [{ x: 10, y: 10 }];
        this.food = this.generateFood();
        this.dx = 0;
        this.dy = 0;
        this.score = 0;
        this.highScore = parseInt(localStorage.getItem('snakeHighScore')) || 0;
        this.level = 1;
        this.gameSpeed = 150;
        this.isPlaying = false;
        this.isPaused = false;
        this.gameLoop = null;
        this.foodEaten = 0;
        this.achievements = new Set(JSON.parse(localStorage.getItem('snakeAchievements') || '[]'));

        // DOM elements
        this.scoreElement = document.getElementById('score');
        this.highScoreElement = document.getElementById('highScore');
        this.levelElement = document.getElementById('level');
        this.snakeLengthElement = document.getElementById('snakeLength');
        this.gameSpeedElement = document.getElementById('gameSpeed');
        this.foodEatenElement = document.getElementById('foodEaten');
        this.gameOverlay = document.getElementById('gameOverlay');
        this.overlayTitle = document.getElementById('overlayTitle');
        this.overlayMessage = document.getElementById('overlayMessage');
        this.startButton = document.getElementById('startButton');
        this.restartButton = document.getElementById('restartButton');
        this.achievementsContainer = document.getElementById('achievements');

        // Sound effects (using Web Audio API)
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        this.init();
    }

    init() {
        this.updateDisplay();
        this.setupEventListeners();
        this.displayAchievements();
        this.draw();
    }

    setupEventListeners() {
        // Keyboard controls
        document.addEventListener('keydown', (e) => {
            if (!this.isPlaying && !this.isPaused) return;
            
            switch(e.key) {
                case 'ArrowUp':
                case 'w':
                case 'W':
                    e.preventDefault();
                    this.changeDirection(0, -1);
                    break;
                case 'ArrowDown':
                case 's':
                case 'S':
                    e.preventDefault();
                    this.changeDirection(0, 1);
                    break;
                case 'ArrowLeft':
                case 'a':
                case 'A':
                    e.preventDefault();
                    this.changeDirection(-1, 0);
                    break;
                case 'ArrowRight':
                case 'd':
                case 'D':
                    e.preventDefault();
                    this.changeDirection(1, 0);
                    break;
                case ' ':
                    e.preventDefault();
                    this.togglePause();
                    break;
                case 'Escape':
                    e.preventDefault();
                    if (this.isPlaying) this.gameOver();
                    break;
            }
        });

        // Button controls
        this.startButton.addEventListener('click', () => this.startGame());
        this.restartButton.addEventListener('click', () => this.restartGame());

        // Mobile controls
        document.getElementById('upBtn').addEventListener('click', () => this.changeDirection(0, -1));
        document.getElementById('downBtn').addEventListener('click', () => this.changeDirection(0, 1));
        document.getElementById('leftBtn').addEventListener('click', () => this.changeDirection(-1, 0));
        document.getElementById('rightBtn').addEventListener('click', () => this.changeDirection(1, 0));
        document.getElementById('pauseBtn').addEventListener('click', () => this.togglePause());

        // Prevent context menu on canvas
        this.canvas.addEventListener('contextmenu', (e) => e.preventDefault());
    }

    changeDirection(newDx, newDy) {
        // Prevent reversing into itself
        if (this.dx === -newDx && this.dy === -newDy) return;
        
        this.dx = newDx;
        this.dy = newDy;
    }

    generateFood() {
        let food;
        do {
            food = {
                x: Math.floor(Math.random() * this.tileCount),
                y: Math.floor(Math.random() * this.tileCount)
            };
        } while (this.snake.some(segment => segment.x === food.x && segment.y === food.y));
        
        return food;
    }

    startGame() {
        this.isPlaying = true;
        this.isPaused = false;
        this.dx = 1;
        this.dy = 0;
        this.gameOverlay.classList.add('hidden');
        this.gameLoop = setInterval(() => this.update(), this.gameSpeed);
        this.playSound('start');
    }

    restartGame() {
        this.resetGame();
        this.startGame();
    }

    resetGame() {
        clearInterval(this.gameLoop);
        this.snake = [{ x: 10, y: 10 }];
        this.food = this.generateFood();
        this.dx = 0;
        this.dy = 0;
        this.score = 0;
        this.level = 1;
        this.gameSpeed = 150;
        this.isPlaying = false;
        this.isPaused = false;
        this.foodEaten = 0;
        this.updateDisplay();
        this.draw();
    }

    togglePause() {
        if (!this.isPlaying) return;
        
        this.isPaused = !this.isPaused;
        
        if (this.isPaused) {
            clearInterval(this.gameLoop);
            this.overlayTitle.textContent = 'Game Paused';
            this.overlayMessage.textContent = 'Press SPACE to resume or click the button below';
            this.startButton.textContent = 'Resume';
            this.startButton.classList.remove('hidden');
            this.restartButton.classList.add('hidden');
            this.gameOverlay.classList.remove('hidden');
        } else {
            this.gameOverlay.classList.add('hidden');
            this.gameLoop = setInterval(() => this.update(), this.gameSpeed);
        }
    }

    update() {
        if (this.isPaused) return;

        // Move snake head
        const head = { x: this.snake[0].x + this.dx, y: this.snake[0].y + this.dy };

        // Check wall collision
        if (head.x < 0 || head.x >= this.tileCount || head.y < 0 || head.y >= this.tileCount) {
            this.gameOver();
            return;
        }

        // Check self collision
        if (this.snake.some(segment => segment.x === head.x && segment.y === head.y)) {
            this.gameOver();
            return;
        }

        this.snake.unshift(head);

        // Check food collision
        if (head.x === this.food.x && head.y === this.food.y) {
            this.eatFood();
        } else {
            this.snake.pop();
        }

        this.draw();
    }

    eatFood() {
        this.score += 10 * this.level;
        this.foodEaten++;
        this.food = this.generateFood();
        this.playSound('eat');
        
        // Increase level every 5 foods
        if (this.foodEaten % 5 === 0) {
            this.levelUp();
        }
        
        this.checkAchievements();
        this.updateDisplay();
    }

    levelUp() {
        this.level++;
        this.gameSpeed = Math.max(80, this.gameSpeed - 10);
        clearInterval(this.gameLoop);
        this.gameLoop = setInterval(() => this.update(), this.gameSpeed);
        this.playSound('levelup');
        this.showTemporaryMessage(`Level ${this.level}!`);
    }

    checkAchievements() {
        const newAchievements = [];
        
        // First food
        if (this.foodEaten === 1 && !this.achievements.has('first-food')) {
            newAchievements.push({ id: 'first-food', text: '🍎 First Bite!' });
        }
        
        // Score milestones
        if (this.score >= 100 && !this.achievements.has('score-100')) {
            newAchievements.push({ id: 'score-100', text: '💯 Century!' });
        }
        if (this.score >= 500 && !this.achievements.has('score-500')) {
            newAchievements.push({ id: 'score-500', text: '🔥 On Fire!' });
        }
        if (this.score >= 1000 && !this.achievements.has('score-1000')) {
            newAchievements.push({ id: 'score-1000', text: '🏆 Master!' });
        }
        
        // Snake length
        if (this.snake.length >= 10 && !this.achievements.has('length-10')) {
            newAchievements.push({ id: 'length-10', text: '🐍 Growing Strong!' });
        }
        if (this.snake.length >= 20 && !this.achievements.has('length-20')) {
            newAchievements.push({ id: 'length-20', text: '🐲 Dragon Size!' });
        }
        
        // Level achievements
        if (this.level >= 5 && !this.achievements.has('level-5')) {
            newAchievements.push({ id: 'level-5', text: '⚡ Speed Demon!' });
        }
        if (this.level >= 10 && !this.achievements.has('level-10')) {
            newAchievements.push({ id: 'level-10', text: '🚀 Lightning Fast!' });
        }
        
        // Add new achievements
        newAchievements.forEach(achievement => {
            this.achievements.add(achievement.id);
            this.showAchievement(achievement.text);
        });
        
        if (newAchievements.length > 0) {
            localStorage.setItem('snakeAchievements', JSON.stringify([...this.achievements]));
            this.displayAchievements();
        }
    }

    showAchievement(text) {
        const achievement = document.createElement('div');
        achievement.className = 'achievement';
        achievement.textContent = text;
        this.achievementsContainer.appendChild(achievement);
        
        // Remove after 3 seconds
        setTimeout(() => {
            if (achievement.parentNode) {
                achievement.parentNode.removeChild(achievement);
            }
        }, 3000);
    }

    displayAchievements() {
        const achievementTexts = {
            'first-food': '🍎 First Bite!',
            'score-100': '💯 Century!',
            'score-500': '🔥 On Fire!',
            'score-1000': '🏆 Master!',
            'length-10': '🐍 Growing Strong!',
            'length-20': '🐲 Dragon Size!',
            'level-5': '⚡ Speed Demon!',
            'level-10': '🚀 Lightning Fast!'
        };
        
        // Clear existing permanent achievements
        this.achievementsContainer.innerHTML = '';
        
        // Add permanent achievement display
        [...this.achievements].forEach(id => {
            if (achievementTexts[id]) {
                const achievement = document.createElement('div');
                achievement.className = 'achievement';
                achievement.textContent = achievementTexts[id];
                achievement.style.opacity = '0.7';
                achievement.style.fontSize = '0.8rem';
                this.achievementsContainer.appendChild(achievement);
            }
        });
    }

    showTemporaryMessage(text) {
        const message = document.createElement('div');
        message.style.position = 'absolute';
        message.style.top = '50%';
        message.style.left = '50%';
        message.style.transform = 'translate(-50%, -50%)';
        message.style.background = 'rgba(0, 0, 0, 0.8)';
        message.style.color = 'white';
        message.style.padding = '20px';
        message.style.borderRadius = '10px';
        message.style.fontSize = '1.5rem';
        message.style.fontWeight = 'bold';
        message.style.zIndex = '20';
        message.textContent = text;
        
        this.canvas.parentNode.appendChild(message);
        
        setTimeout(() => {
            if (message.parentNode) {
                message.parentNode.removeChild(message);
            }
        }, 1500);
    }

    gameOver() {
        clearInterval(this.gameLoop);
        this.isPlaying = false;
        this.isPaused = false;
        
        // Update high score
        if (this.score > this.highScore) {
            this.highScore = this.score;
            localStorage.setItem('snakeHighScore', this.highScore.toString());
            this.showTemporaryMessage('New High Score!');
        }
        
        this.playSound('gameOver');
        this.canvas.classList.add('game-over');
        
        setTimeout(() => {
            this.canvas.classList.remove('game-over');
            this.overlayTitle.textContent = 'Game Over!';
            this.overlayMessage.textContent = `Score: ${this.score} | Length: ${this.snake.length} | Level: ${this.level}`;
            this.startButton.classList.add('hidden');
            this.restartButton.classList.remove('hidden');
            this.gameOverlay.classList.remove('hidden');
        }, 500);
        
        this.updateDisplay();
    }

    draw() {
        // Clear canvas
        this.ctx.fillStyle = '#1a202c';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

        // Draw grid (subtle)
        this.ctx.strokeStyle = 'rgba(255, 255, 255, 0.1)';
        this.ctx.lineWidth = 1;
        for (let i = 0; i <= this.tileCount; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.gridSize, 0);
            this.ctx.lineTo(i * this.gridSize, this.canvas.height);
            this.ctx.stroke();
            
            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.gridSize);
            this.ctx.lineTo(this.canvas.width, i * this.gridSize);
            this.ctx.stroke();
        }

        // Draw snake
        this.snake.forEach((segment, index) => {
            if (index === 0) {
                // Snake head
                this.ctx.fillStyle = '#48bb78';
                this.ctx.fillRect(
                    segment.x * this.gridSize + 2,
                    segment.y * this.gridSize + 2,
                    this.gridSize - 4,
                    this.gridSize - 4
                );
                
                // Eyes
                this.ctx.fillStyle = '#1a202c';
                this.ctx.fillRect(
                    segment.x * this.gridSize + 6,
                    segment.y * this.gridSize + 6,
                    3, 3
                );
                this.ctx.fillRect(
                    segment.x * this.gridSize + 11,
                    segment.y * this.gridSize + 6,
                    3, 3
                );
            } else {
                // Snake body
                const alpha = Math.max(0.3, 1 - (index * 0.05));
                this.ctx.fillStyle = `rgba(72, 187, 120, ${alpha})`;
                this.ctx.fillRect(
                    segment.x * this.gridSize + 2,
                    segment.y * this.gridSize + 2,
                    this.gridSize - 4,
                    this.gridSize - 4
                );
            }
        });

        // Draw food with animation
        const time = Date.now() * 0.01;
        const pulse = Math.sin(time) * 0.1 + 0.9;
        this.ctx.fillStyle = '#f56565';
        const foodSize = (this.gridSize - 4) * pulse;
        const offset = (this.gridSize - foodSize) / 2;
        
        this.ctx.fillRect(
            this.food.x * this.gridSize + offset,
            this.food.y * this.gridSize + offset,
            foodSize,
            foodSize
        );
    }

    updateDisplay() {
        this.scoreElement.textContent = this.score;
        this.highScoreElement.textContent = this.highScore;
        this.levelElement.textContent = this.level;
        this.snakeLengthElement.textContent = this.snake.length;
        this.foodEatenElement.textContent = this.foodEaten;
        
        // Update speed display
        if (this.gameSpeed > 120) {
            this.gameSpeedElement.textContent = 'Normal';
        } else if (this.gameSpeed > 100) {
            this.gameSpeedElement.textContent = 'Fast';
        } else {
            this.gameSpeedElement.textContent = 'Very Fast';
        }
    }

    playSound(type) {
        // Simple sound generation using Web Audio API
        try {
            const oscillator = this.audioContext.createOscillator();
            const gainNode = this.audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(this.audioContext.destination);
            
            switch(type) {
                case 'eat':
                    oscillator.frequency.value = 800;
                    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.1);
                    break;
                case 'gameOver':
                    oscillator.frequency.value = 200;
                    gainNode.gain.setValueAtTime(0.2, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.5);
                    break;
                case 'levelup':
                    oscillator.frequency.value = 1000;
                    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.3);
                    break;
                case 'start':
                    oscillator.frequency.value = 600;
                    gainNode.gain.setValueAtTime(0.1, this.audioContext.currentTime);
                    gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + 0.2);
                    break;
            }
            
            oscillator.start(this.audioContext.currentTime);
            oscillator.stop(this.audioContext.currentTime + 0.5);
        } catch (error) {
            // Audio context might not be available
            console.log('Audio not available');
        }
    }
}

// Initialize game when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new SnakeGame();
});

// Handle visibility change (pause when tab is hidden)
document.addEventListener('visibilitychange', () => {
    if (document.hidden && window.game && window.game.isPlaying && !window.game.isPaused) {
        window.game.togglePause();
    }
});

// Expose game instance globally for debugging
window.addEventListener('load', () => {
    if (window.game) {
        window.game = game;
    }
});
