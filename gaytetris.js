// game.js
// ... (previous constants remain the same) ...
// game.js
const BLOCK_SIZE = 30;
const GRID_WIDTH = 10;
const GRID_HEIGHT = 20;

const COLORS = [
    0xff61a6, // Pink
    0x7e57c2, // Purple
    0x2196f3, // Blue
    0xff4081, // Hot Pink
    0xab47bc, // Violet
    0x64b5f6, // Light Blue
    0xf06292  // Rose
];

const COMPLIMENTS = [
    "You're a radiant star! ⭐",
    "Your energy is absolutely fabulous! 💖",
    "You're serving pure excellence! 👑",
    "Werk it, divine being! ✨",
    "You're slaying this game, queen! 💅",
    "Your aura is absolutely magical! 🌟",
    "You're giving me life right now! 🎉",
    "Fierce and flawless, honey! 💃",
    "You're a goddess walking among us! 👸",
    "Your presence is everything! ✨",
    "Stunning and brave, darling! 💖",
    "You're the moment! 🌈",
    "Main character energy! 🎭",
    "You're giving butterfly goddess! 🦋",
    "Pure excellence incarnate! 👑",
    "Your power is unmatched! ⚡",
    "Iconic behavior! 💫",
    "You're literally glowing! ✨",
    "Serving face and grace! 💅",
    "You're the blueprint! 📝",
    "Living art, honestly! 🎨",
    "Standard of beauty! 💖",
    "You ate and left no crumbs! 💫",
    "The moment is yours! 🌟",
    "Your mind is so powerful! 🧠",
    "You're giving everything! 💝",
    "Legend behavior only! 👑",
    "Pure goddess energy! ✨",
    "You're the divine feminine! 🌙",
    "Main pop girl behavior! 💫",
    "Your power is limitless! ⚡",
    "Absolutely ethereal! 🧚‍♀️",
    "You're the fantasy! 🌈",
    "Giving celestial beauty! ⭐",
    "Pure magic in human form! ✨",
    "You're the moment! 💫",
    "Unstoppable queen vibes! 👑",
    "Your essence is divine! 🌟",
    "Serving face for days! 💅",
    "You're the standard! 💖",
    "That's on period! 💫",
    "Nature's finest work! 🌸",
    "The blueprint herself! 📝",
    "Giving goddess realness! ✨",
    "Your power is immaculate! ⚡",
    "Pure excellence! 💫",
    "You're the definition of grace! 🦢",
    "Iconic status achieved! 🌟",
    "Blessing us with your presence! 👑",
    "You're the moment, sweetie! 💖"
];

class TetrisScene extends Phaser.Scene {
    constructor() {
        super({ key: 'TetrisScene' });
        this.lastMoveTime = 0;
        this.moveDelay = 200; // 0.2 seconds
        this.holdPiece = null;
        this.canHold = true;
        this.particles = null;
        this.rainbowColors = [0xff0000, 0xff7f00, 0xffff00, 0x00ff00, 0x0000ff, 0x4b0082, 0x9400d3];
        this.rainbowIndex = 0;
    }

    preload() {
        // Load sound effects
        this.load.audio('rotate', 'https://cdn.pixabay.com/download/audio/2022/03/24/audio_c8c8a73467.mp3');
        this.load.audio('move', 'https://cdn.pixabay.com/download/audio/2022/03/24/audio_c8c8a73467.mp3');
        this.load.audio('drop', 'https://cdn.pixabay.com/download/audio/2022/03/24/audio_c8c8a73467.mp3');
        this.load.audio('clear', 'https://cdn.pixabay.com/download/audio/2022/03/24/audio_c8c8a73467.mp3');
        
        // Create block texture
        const graphics = this.add.graphics();
        graphics.fillStyle(0xffffff);
        graphics.fillRect(0, 0, BLOCK_SIZE - 2, BLOCK_SIZE - 2);
        graphics.generateTexture('block', BLOCK_SIZE, BLOCK_SIZE);
        graphics.destroy();

        // Create sparkle texture
        const sparkle = this.add.graphics();
        sparkle.lineStyle(2, 0xffffff);
        sparkle.beginPath();
        sparkle.moveTo(0, 5);
        sparkle.lineTo(10, 5);
        sparkle.moveTo(5, 0);
        sparkle.lineTo(5, 10);
        sparkle.strokePath();
        sparkle.generateTexture('sparkle', 10, 10);
        sparkle.destroy();
    }

    create() {
        // ... (previous create code) ...
        this.grid = Array(GRID_HEIGHT).fill().map(() => Array(GRID_WIDTH).fill(null));
        this.currentPiece = null;
        this.gameOver = false;
        this.score = 0;

        // Create game border with gradient
        const border = this.add.graphics();
        border.lineGradientStyle(4, 0xff61a6, 0x7e57c2, 0x2196f3, 0xff61a6);
        border.strokeRect(0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE);

        // Score text with fabulous style
        this.scoreText = this.add.text(GRID_WIDTH * BLOCK_SIZE + 20, 20, 'Score: 0', {
            fontFamily: 'Arial',
            fontSize: '24px',
            fill: '#ffffff',
            stroke: '#ff61a6',
            strokeThickness: 2
        });

        // Compliment text
        this.complimentText = this.add.text(GRID_WIDTH * BLOCK_SIZE / 2, GRID_HEIGHT * BLOCK_SIZE + 30, '', {
            fontFamily: 'Arial',
            fontSize: '18px',
            fill: '#ffffff',
            align: 'center'
        }).setOrigin(0.5);

        // Input handling
        this.cursors = this.input.keyboard.createCursorKeys();
        
        // Start game
        this.spawnPiece();
        this.time.addEvent({
            delay: 1000,
            callback: this.moveDown,
            callbackScope: this,
            loop: true
        });
        // Initialize particle system
        this.particles = this.add.particles('sparkle');

        // Add hold piece display
        this.holdBox = this.add.graphics();
        this.holdBox.lineStyle(2, 0xff61a6);
        this.holdBox.strokeRect(GRID_WIDTH * BLOCK_SIZE + 20, 100, BLOCK_SIZE * 4, BLOCK_SIZE * 4);
        this.add.text(GRID_WIDTH * BLOCK_SIZE + 20, 70, 'Hold (H)', {
            fontFamily: 'Arial',
            fontSize: '18px',
            fill: '#ffffff'
        });

        // Add rainbow gradient background
        this.rainbowBackground = this.add.graphics();
        this.time.addEvent({
            delay: 50,
            callback: this.updateRainbowBackground,
            callbackScope: this,
            loop: true
        });

        // Enhanced input handling
        this.keys = this.input.keyboard.addKeys({
            up: 'UP',
            down: 'DOWN',
            left: 'LEFT',
            right: 'RIGHT',
            w: 'W',
            a: 'A',
            s: 'S',
            d: 'D',
            h: 'H'
        });
    }
    spawnPiece() {
        const pieces = [
            [[1, 1, 1, 1]], // I
            [[1, 1], [1, 1]], // O
            [[1, 1, 1], [0, 1, 0]], // T
            [[1, 1, 1], [1, 0, 0]], // L
            [[1, 1, 1], [0, 0, 1]], // J
            [[1, 1, 0], [0, 1, 1]], // S
            [[0, 1, 1], [1, 1, 0]]  // Z
        ];

        this.currentPiece = {
            shape: Phaser.Utils.Array.GetRandom(pieces),
            x: Math.floor(GRID_WIDTH / 2) - 1,
            y: 0,
            color: Phaser.Utils.Array.GetRandom(COLORS)
        };

        if (this.checkCollision()) {
            this.gameOver = true;
        }
    }

    showRandomCompliment() {
        const compliment = Phaser.Utils.Array.GetRandom(COMPLIMENTS);
        this.complimentText.setText(compliment);
        
        // Add sparkle effect
        this.createSparkles();
        
        // Animate compliment
        this.tweens.add({
            targets: this.complimentText,
            scaleX: 1.2,
            scaleY: 1.2,
            duration: 200,
            yoyo: true
        });
    }

    createSparkles() {
        for (let i = 0; i < 10; i++) {
            const x = Phaser.Math.Between(0, GRID_WIDTH * BLOCK_SIZE);
            const y = Phaser.Math.Between(0, GRID_HEIGHT * BLOCK_SIZE);
            
            const sparkle = this.add.star(x, y, 5, 2, 4, 0xffffff);
            
            this.tweens.add({
                targets: sparkle,
                alpha: 0,
                scale: 0,
                duration: 1000,
                onComplete: () => sparkle.destroy()
            });
        }
    }

    updateRainbowBackground() {
        this.rainbowIndex = (this.rainbowIndex + 1) % this.rainbowColors.length;
        const gradient = this.rainbowBackground;
        gradient.clear();
        gradient.lineGradientStyle(
            4,
            this.rainbowColors[this.rainbowIndex],
            this.rainbowColors[(this.rainbowIndex + 1) % this.rainbowColors.length],
            this.rainbowColors[(this.rainbowIndex + 2) % this.rainbowColors.length],
            this.rainbowColors[(this.rainbowIndex + 3) % this.rainbowColors.length]
        );
        gradient.strokeRect(0, 0, GRID_WIDTH * BLOCK_SIZE, GRID_HEIGHT * BLOCK_SIZE);
    }

    hardDrop() {
        let dropDistance = 0;
        while (!this.checkCollision()) {
            this.currentPiece.y++;
            dropDistance++;
        }
        this.currentPiece.y--;
        this.lockPiece();
        this.clearLines();
        this.spawnPiece();
        this.showRandomCompliment();
        //this.sound.play('drop');
        
        // Create particle trail effect
        for (let i = 0; i < dropDistance; i++) {
            this.createTrailEffect(this.currentPiece.x * BLOCK_SIZE, (this.currentPiece.y - i) * BLOCK_SIZE);
        }
    }

    createTrailEffect(x, y) {
        this.particles.createEmitter({
            x: x,
            y: y,
            speed: { min: -100, max: 100 },
            angle: { min: 0, max: 360 },
            scale: { start: 0.5, end: 0 },
            lifespan: 1000,
            quantity: 1,
            frequency: 50
        });
    }

    holdPieceFunction() {
        if (!this.canHold) return;
        
        const temp = this.currentPiece;
        if (this.holdPiece === null) {
            this.holdPiece = {
                shape: temp.shape,
                color: temp.color
            };
            this.spawnPiece();
        } else {
            this.currentPiece = {
                shape: this.holdPiece.shape,
                color: this.holdPiece.color,
                x: Math.floor(GRID_WIDTH / 2) - 1,
                y: 0
            };
            this.holdPiece = {
                shape: temp.shape,
                color: temp.color
            };
        }
        
        this.canHold = false;
        this.createHoldEffect();
    }

    createHoldEffect() {
        const x = GRID_WIDTH * BLOCK_SIZE + 60;
        const y = 120;
        
        const emitter = this.particles.createEmitter({
            x: x,
            y: y,
            speed: { min: 100, max: 200 },
            angle: { min: 0, max: 360 },
            scale: { start: 1, end: 0 },
            lifespan: 1000,
            quantity: 20
        });

        this.time.delayedCall(1000, () => emitter.stop());
    }

    createLinesClearEffect(y) {
        const emitter = this.particles.createEmitter({
            x: { min: 0, max: GRID_WIDTH * BLOCK_SIZE },
            y: y * BLOCK_SIZE,
            speedX: { min: -100, max: 100 },
            speedY: { min: -100, max: 100 },
            scale: { start: 1, end: 0 },
            lifespan: 1000,
            quantity: 50,
            tint: this.rainbowColors
        });

        this.time.delayedCall(1000, () => emitter.stop());
    }

    update(time) {
        if (this.gameOver) {
            this.createGameOverEffect();
            return;
        }

        // Movement with rate limiting
        if (time - this.lastMoveTime >= this.moveDelay) {
            if (this.keys.left.isDown) {
                this.moveLeft();
                this.lastMoveTime = time;
            } else if (this.keys.right.isDown) {
                this.moveRight();
                this.lastMoveTime = time;
            }
        }

        // Hard drop with 'up' or 'w'
        if (Phaser.Input.Keyboard.JustDown(this.keys.up) || 
            Phaser.Input.Keyboard.JustDown(this.keys.w)) {
            this.hardDrop();
        }

        // Rotations
        if (Phaser.Input.Keyboard.JustDown(this.keys.a)) {
            this.rotatePiece('clockwise');
            //this.sound.play('rotate');
        }
        if (Phaser.Input.Keyboard.JustDown(this.keys.d)) {
            this.rotatePiece('counterclockwise');
            //this.sound.play('rotate');
        }

        // Hold piece
        if (Phaser.Input.Keyboard.JustDown(this.keys.h)) {
            this.holdPieceFunction();
        }

        if (this.keys.down.isDown) {
            this.moveDown();
        }

        this.drawGame();
    }
    moveLeft() {
        this.currentPiece.x--;
        if (this.checkCollision()) this.currentPiece.x++;
    }

    moveRight() {
        this.currentPiece.x++;
        if (this.checkCollision()) this.currentPiece.x--;
    }

    moveDown() {
        if (!this.currentPiece || this.gameOver) return;
        
        this.currentPiece.y++;
        if (this.checkCollision()) {
            this.currentPiece.y--;
            this.lockPiece();
            this.clearLines();
            this.spawnPiece();
            this.showRandomCompliment();
        }
    }

    checkCollision() {
        return this.currentPiece.shape.some((row, y) =>
            row.some((cell, x) => {
                if (!cell) return false;
                
                const gridX = this.currentPiece.x + x;
                const gridY = this.currentPiece.y + y;
                
                return gridX < 0 || 
                       gridX >= GRID_WIDTH ||
                       gridY >= GRID_HEIGHT ||
                       (gridY >= 0 && this.grid[gridY][gridX]);
            })
        );
    }

    lockPiece() {
        this.currentPiece.shape.forEach((row, y) => {
            row.forEach((cell, x) => {
                if (cell) {
                    const gridY = this.currentPiece.y + y;
                    if (gridY >= 0) {
                        this.grid[gridY][this.currentPiece.x + x] = this.currentPiece.color;
                    }
                }
            });
        });
    }

    rotatePiece(direction) {
        if (!this.currentPiece) return;
        
        const rotated = direction === 'clockwise' 
            ? this.currentPiece.shape[0].map((_, i) =>
                this.currentPiece.shape.map(row => row[row.length - 1 - i]))
            : this.currentPiece.shape[0].map((_, i) =>
                this.currentPiece.shape.map(row => row[i]).reverse());
        
        const oldShape = this.currentPiece.shape;
        this.currentPiece.shape = rotated;
        
        if (this.checkCollision()) {
            this.currentPiece.shape = oldShape;
        } else {
            this.createRotateEffect();
        }
    }

    createRotateEffect() {
        const centerX = (this.currentPiece.x + this.currentPiece.shape[0].length/2) * BLOCK_SIZE;
        const centerY = (this.currentPiece.y + this.currentPiece.shape.length/2) * BLOCK_SIZE;
        
        const emitter = this.particles.createEmitter({
            x: centerX,
            y: centerY,
            speed: 100,
            angle: { min: 0, max: 360 },
            scale: { start: 0.5, end: 0 },
            lifespan: 500,
            quantity: 10
        });

        this.time.delayedCall(500, () => emitter.stop());
    }

    createGameOverEffect() {
        // Create expanding ring effect
        const centerX = GRID_WIDTH * BLOCK_SIZE / 2;
        const centerY = GRID_HEIGHT * BLOCK_SIZE / 2;
        
        const emitter = this.particles.createEmitter({
            x: centerX,
            y: centerY,
            speed: { min: 200, max: 400 },
            angle: { min: 0, max: 360 },
            scale: { start: 1, end: 0 },
            lifespan: 2000,
            quantity: 100,
            tint: this.rainbowColors
        });

        this.time.delayedCall(2000, () => emitter.stop());
    }

    clearLines() {
        let linesCleared = 0;
        
        for (let y = GRID_HEIGHT - 1; y >= 0; y--) {
            if (this.grid[y].every(cell => cell !== null)) {
                this.createLinesClearEffect(y);
                this.grid.splice(y, 1);
                this.grid.unshift(Array(GRID_WIDTH).fill(null));
                linesCleared++;
                y++;
                
                // Play clear sound with increasing pitch for combos
                //this.sound.play('clear', {
                //    rate: 1 + (linesCleared * 0.1)
                //});
            }
        }
        
        if (linesCleared > 0) {
            this.score += linesCleared * 100 * linesCleared; // Bonus for multiple lines
            this.scoreText.setText(`Score: ${this.score}`);
            
            // Reset hold ability after clearing lines
            this.canHold = true;
        }
    }

    drawGame() {
        // ... (previous draw code) ...
        // Clear previous frame
        this.children.list
            .filter(child => child instanceof Phaser.GameObjects.Image)
            .forEach(child => child.destroy());

        // Draw locked pieces
        this.grid.forEach((row, y) => {
            row.forEach((color, x) => {
                if (color !== null) {
                    this.add.image(x * BLOCK_SIZE + BLOCK_SIZE/2, 
                                 y * BLOCK_SIZE + BLOCK_SIZE/2, 'block')
                        .setTint(color);
                }
            });
        });

        // Draw current piece
        if (this.currentPiece) {
            this.currentPiece.shape.forEach((row, y) => {
                row.forEach((cell, x) => {
                    if (cell) {
                        this.add.image((this.currentPiece.x + x) * BLOCK_SIZE + BLOCK_SIZE/2,
                                     (this.currentPiece.y + y) * BLOCK_SIZE + BLOCK_SIZE/2, 'block')
                            .setTint(this.currentPiece.color);
                    }
                });
            });
        }
        // Draw hold piece
        if (this.holdPiece) {
            const holdX = GRID_WIDTH * BLOCK_SIZE + 40;
            const holdY = 120;
            
            this.holdPiece.shape.forEach((row, y) => {
                row.forEach((cell, x) => {
                    if (cell) {
                        this.add.image(holdX + x * BLOCK_SIZE,
                                     holdY + y * BLOCK_SIZE,
                                     'block')
                            .setTint(this.holdPiece.color)
                            .setAlpha(this.canHold ? 1 : 0.5);
                    }
                });
            });
        }
    }
}


const config = {
    type: Phaser.AUTO,
    width: BLOCK_SIZE * (GRID_WIDTH + 8),
    height: BLOCK_SIZE * (GRID_HEIGHT + 2),
    parent: 'game-container',
    backgroundColor: '#1a1a1a',
    scene: TetrisScene
};

const game = new Phaser.Game(config);