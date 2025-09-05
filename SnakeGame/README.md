# 🐍 Snake Game - Classic Arcade Clone

A modern, responsive implementation of the classic Snake game built with HTML5 Canvas, CSS3, and vanilla JavaScript. Features a beautiful UI, smooth gameplay, achievements system, and mobile support.

![Snake Game](https://img.shields.io/badge/Game-Snake-green)
![HTML5](https://img.shields.io/badge/HTML5-Canvas-orange)
![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-yellow)
![CSS3](https://img.shields.io/badge/CSS3-Responsive-blue)

## ✨ Features

### 🎮 **Core Gameplay**
- Classic Snake mechanics with smooth movement
- Progressive difficulty - speed increases with level
- Collision detection for walls and self-collision
- Score system with level bonuses
- High score persistence using localStorage

### 🎨 **Modern UI/UX**
- Beautiful gradient backgrounds and glass-morphism effects
- Responsive design that works on desktop and mobile
- Smooth animations and visual feedback
- Real-time statistics display
- Animated food with pulsing effect
- Game over animations and effects

### 🏆 **Achievement System**
- 8 different achievements to unlock
- Persistent achievement tracking
- Visual achievement notifications
- Achievement gallery display

### 🎵 **Audio Experience**
- Dynamic sound effects using Web Audio API
- Different sounds for eating, game over, level up, and start
- No external audio files required

### 📱 **Mobile Support**
- Touch-friendly mobile controls
- Responsive canvas that scales properly
- Optimized for different screen sizes
- Prevent accidental context menus and selections

### ⌨️ **Controls**
- **Arrow Keys** or **WASD** for movement
- **Spacebar** to pause/resume
- **Escape** to quit current game
- **Mobile touch controls** for mobile devices

## 🚀 Quick Start

### Prerequisites
- Modern web browser with HTML5 Canvas support
- No additional dependencies required

### Installation

1. **Clone or download the files**
   ```bash
   # If using git
   git clone <repository-url>
   cd SnakeGame
   ```

2. **Open the game**
   - Simply open `index.html` in any modern web browser
   - Or serve it through a local web server:
   ```bash
   # Using Python (if installed)
   python -m http.server 8000
   
   # Using Node.js (if installed)
   npx serve .
   ```

3. **Start playing!**
   - Click "Start Game" or press any arrow key
   - Use arrow keys or WASD to control the snake
   - Eat red food to grow and increase your score

## 📁 File Structure

```
SnakeGame/
├── index.html          # Main game page with UI structure
├── style.css           # Responsive styles and animations
├── script.js           # Complete game logic and mechanics
└── README.md           # This documentation
```

## 🎯 Game Mechanics

### Scoring System
- **10 points** per food eaten (base score)
- **Multiplied by current level** for bonus points
- Example: Level 3 food = 30 points

### Level Progression
- **Level increases** every 5 foods eaten
- **Speed increases** with each level (faster gameplay)
- **Maximum speed** cap prevents impossible gameplay

### Achievements
| Achievement | Requirement | Reward |
|-------------|-------------|---------|
| 🍎 First Bite! | Eat your first food | Getting started |
| 💯 Century! | Score 100+ points | Basic milestone |
| 🔥 On Fire! | Score 500+ points | Intermediate skill |
| 🏆 Master! | Score 1000+ points | Advanced gameplay |
| 🐍 Growing Strong! | Snake length 10+ | Length milestone |
| 🐲 Dragon Size! | Snake length 20+ | Maximum growth |
| ⚡ Speed Demon! | Reach level 5 | Speed milestone |
| 🚀 Lightning Fast! | Reach level 10 | Ultimate speed |

## 🛠️ Technical Implementation

### Architecture
- **Object-Oriented Design**: Single `SnakeGame` class encapsulates all functionality
- **Canvas Rendering**: Smooth 60fps gameplay with custom drawing
- **Event-Driven**: Keyboard and touch event handling
- **State Management**: Clean game state transitions

### Key Technologies
- **HTML5 Canvas**: For game rendering and animations
- **CSS3**: Modern styling with gradients, shadows, and responsive design
- **Vanilla JavaScript**: No external dependencies, pure ES6+
- **Web Audio API**: Dynamic sound generation
- **LocalStorage**: High score and achievement persistence

### Performance Features
- **Efficient collision detection** using coordinate comparison
- **Optimized rendering** with minimal canvas operations
- **Memory management** with proper event cleanup
- **Responsive frame rate** independent of game speed

## 🎨 Customization

### Modifying Game Parameters
Edit these values in `script.js`:

```javascript
// Game speed (lower = faster)
this.gameSpeed = 150;  // Starting speed in milliseconds

// Grid size
this.gridSize = 20;    // Size of each game tile

// Level progression
if (this.foodEaten % 5 === 0) {  // Change 5 to adjust level frequency
    this.levelUp();
}

// Speed increase per level
this.gameSpeed = Math.max(80, this.gameSpeed - 10);  // Min speed 80ms
```

### Adding New Achievements
```javascript
// In checkAchievements() method
if (this.score >= 2000 && !this.achievements.has('score-2000')) {
    newAchievements.push({ id: 'score-2000', text: '🌟 Legendary!' });
}
```

### Styling Changes
Modify colors and effects in `style.css`:
```css
/* Change snake color */
.ctx.fillStyle = '#48bb78';  /* Current green */

/* Change food color */
.ctx.fillStyle = '#f56565';  /* Current red */

/* Modify background gradient */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## 📱 Mobile Optimization

The game includes several mobile-specific features:
- **Touch Controls**: Large, easy-to-tap directional buttons
- **Responsive Canvas**: Automatically scales to fit screen
- **Prevent Zoom**: Disabled pinch-to-zoom for better gameplay
- **Orientation Support**: Works in both portrait and landscape
- **Performance**: Optimized for mobile browsers

## 🏆 High Score & Data Persistence

The game automatically saves:
- **High Score**: Best score achieved across all sessions
- **Achievements**: Unlocked achievements persist between games
- **Statistics**: Various gameplay statistics

Data is stored locally in the browser using `localStorage` and will persist until manually cleared.

## 🎮 Why This Project Matters

### For Players
- **Nostalgic Fun**: Classic arcade experience with modern polish
- **Challenging Gameplay**: Progressive difficulty keeps it engaging
- **Achievement System**: Goals and milestones for replayability

### For Developers
- **Clean Code**: Well-structured, commented, and maintainable
- **Modern JavaScript**: ES6+ features and best practices
- **Canvas Mastery**: Advanced HTML5 Canvas techniques
- **Responsive Design**: Mobile-first approach with progressive enhancement
- **Game Development**: Core concepts like game loops, collision detection, and state management

### For Recruiters
- **Technical Skill**: Demonstrates proficiency in frontend technologies
- **Problem Solving**: Game logic, algorithms, and optimization
- **User Experience**: Polished interface and smooth gameplay
- **Attention to Detail**: Sound effects, animations, and responsive design

## 🚀 Potential Enhancements

Future improvements could include:
- **Multiplayer Support**: Real-time competition with other players
- **Power-ups**: Special food items with unique effects
- **Themes**: Different visual themes and snake skins
- **Leaderboards**: Online high score competition
- **AI Snake**: Computer-controlled opponent
- **Custom Maps**: Different game board layouts and obstacles

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs or suggest features
- Submit pull requests for improvements
- Share your high scores and achievements!

## 📞 Support

For questions or support, please open an issue in the repository.

---

**Built with ❤️ for classic arcade game lovers everywhere!** 🐍🎮

*Challenge yourself to beat the high score and unlock all achievements!*
