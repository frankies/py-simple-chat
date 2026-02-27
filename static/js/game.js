/*
Simplified port of the Python game logic to JavaScript.
Handles rendering, input, and state updates in the browser.
*/

class Settings {
    constructor() {
        // screen
        this.screenWidth = 1200;
        this.screenHeight = 800;
        this.bgColor = '#000';

        // ship
        this.shipSpeed = 1.5;
        this.shipLimit = 3;

        // bullet
        this.bulletSpeed = 2.5;
        this.bulletsAllowed = 5;

        // alien
        this.alienSpeed = 0.5;
        this.fleetDropSpeed = 10;
        this.fleetDirection = 1;

        // speedup
        this.speedupScale = 1.1;
        this.scoreScale = 1.5;
    }

    initializeDynamicSettings() {
        this.shipSpeed = 1.5;
        this.bulletSpeed = 2.5;
        this.alienSpeed = 0.5;
        this.fleetDirection = 1;
    }

    increaseSpeed() {
        this.shipSpeed *= this.speedupScale;
        this.bulletSpeed *= this.speedupScale;
        this.alienSpeed *= this.speedupScale;
    }
}

class GameStats {
    constructor() {
        this.resetStats();
        this.gameActive = false;
        this.highScore = 0;
    }
    resetStats() {
        this.shipsLeft = 3;
        this.score = 0;
        this.level = 1;
        this.shipInvincible = false;
    }
}

class Ship {
    constructor(game) {
        this.game = game;
        this.settings = game.settings;
        this.width = 40;
        this.height = 60;
        this.x = (this.settings.screenWidth - this.width) / 2;
        this.y = this.settings.screenHeight - this.height;
        this.movingRight = false;
        this.movingLeft = false;
        this.movingUp = false;
        this.movingDown = false;
        this.invincible = false;
        this.invincibleTimer = 0;
    }
    update() {
        if (this.movingRight && this.x + this.width < this.settings.screenWidth) {
            this.x += this.settings.shipSpeed;
        }
        if (this.movingLeft && this.x > 0) {
            this.x -= this.settings.shipSpeed;
        }
        if (this.movingUp && this.y > 0) {
            this.y -= this.settings.shipSpeed;
        }
        if (this.movingDown && this.y + this.height < this.settings.screenHeight) {
            this.y += this.settings.shipSpeed;
        }
        if (this.invincible) {
            this.invincibleTimer += 1;
            if (this.invincibleTimer > 120) {
                this.invincible = false;
                this.invincibleTimer = 0;
            }
        }
    }
    draw(ctx) {
        ctx.fillStyle = this.invincible && (this.invincibleTimer % 4 < 2) ? 'rgba(255,255,255,0.3)' : '#fff';
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class Bullet {
    constructor(game, fromAlien=false) {
        this.game = game;
        this.settings = game.settings;
        this.fromAlien = fromAlien;
        this.width = 5;
        this.height = 15;
        this.color = fromAlien ? '#f00' : '#fff';
        this.x = fromAlien ? 0 : game.ship.x + game.ship.width/2 - this.width/2;
        this.y = fromAlien ? 0 : game.ship.y;
        if (fromAlien) {
            // vertical position will be set when created
        }
    }
    update() {
        if (this.fromAlien) this.y += this.settings.bulletSpeed;
        else this.y -= this.settings.bulletSpeed;
    }
    draw(ctx) {
        ctx.fillStyle = this.color;
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
}

class Alien {
    constructor(game, type='normal') {
        this.game = game;
        this.settings = game.settings;
        this.type = type;
        this.width = 50;
        this.height = 40;
        this.x = 0;
        this.y = 0;
        this.hp = type === 'blue' ? 2 : 1;
        this.points = type === 'blue' ? 100 : type === 'red' ? 50 : 30;
    }
    update() {
        this.x += this.settings.alienSpeed * this.settings.fleetDirection;
    }
    draw(ctx) {
        if (this.type === 'red') ctx.fillStyle = '#f55';
        else if (this.type === 'blue') ctx.fillStyle = '#55f';
        else ctx.fillStyle = '#0f0';
        ctx.fillRect(this.x, this.y, this.width, this.height);
    }
    checkEdges() {
        return this.x + this.width >= this.settings.screenWidth || this.x <= 0;
    }
}

class Game {
    constructor() {
        this.settings = new Settings();
        this.stats = new GameStats();
        this.ship = new Ship(this);
        this.bullets = [];
        this.alienBullets = [];
        this.aliens = [];
        this.gameActive = false;
        this.gameOver = false;
        this.gameOverTime = 0;
    }
    start() {
        this.settings.initializeDynamicSettings();
        this.stats.resetStats();
        this.gameActive = true;
        this.aliens = [];
        this.bullets = [];
        this.alienBullets = [];
        this.createFleet();
    }
    update() {
        if (this.gameActive && !this.gameOver) {
            this.ship.update();
            this.updateBullets();
            this.updateAliens();
            this.updateAlienBullets();
        }
    }
    createFleet() {
        const base = 6;
        const add = this.stats.level - 1;
        const cols = Math.min(base + add, 11);
        const rows = Math.min(3 + Math.floor(add/2), 5);
        for (let row = 0; row < rows; row++) {
            for (let col = 0; col < cols; col++) {
                const r = Math.random();
                let t = 'normal';
                if (r < 0.1) t = 'red';
                else if (r < 0.2) t = 'blue';
                const a = new Alien(this, t);
                a.x = 60 + col * 80;
                a.y = 60 + row * 70;
                this.aliens.push(a);
            }
        }
    }
    updateBullets() {
        this.bullets.forEach(b => b.update());
        this.bullets = this.bullets.filter(b => b.y + b.height > 0);
        // collision
        this.aliens.forEach(a => {
            this.bullets.forEach((b,i) => {
                if (b.x < a.x + a.width && b.x + b.width > a.x &&
                    b.y < a.y + a.height && b.y + b.height > a.y) {
                    a.hp -= 1;
                    this.bullets.splice(i,1);
                }
            });
        });
        this.aliens = this.aliens.filter(a => {
            if (a.hp <= 0) {
                this.stats.score += a.points;
                return false;
            }
            return true;
        });
        if (this.aliens.length === 0) {
            this.bullets = [];
            this.stats.level += 1;
            this.settings.increaseSpeed();
            this.createFleet();
        }
    }
    updateAliens() {
        let hitEdge = false;
        this.aliens.forEach(a => {
            a.update();
            if (a.checkEdges()) hitEdge = true;
        });
        if (hitEdge) {
            this.aliens.forEach(a => { a.y += 8; });
            this.settings.fleetDirection *= -1;
        }
        if (Math.random() < 0.01 && this.aliens.length) {
            const idx = Math.floor(Math.random() * this.aliens.length);
            const a = this.aliens[idx];
            const b = new Bullet(this, true);
            b.x = a.x + a.width/2 - b.width/2;
            b.y = a.y + a.height;
            this.alienBullets.push(b);
        }
        if (!this.ship.invincible) {
            this.aliens.forEach(a => {
                if (this.collides(this.ship, a)) {
                    this.shipHit();
                }
            });
        }
    }
    updateAlienBullets() {
        this.alienBullets.forEach(b => b.update());
        this.alienBullets = this.alienBullets.filter(b => b.y < this.settings.screenHeight);
        if (!this.ship.invincible) {
            this.alienBullets.forEach((b,i) => {
                if (this.collides(this.ship,b)) {
                    this.alienBullets.splice(i,1);
                    this.shipHit();
                }
            });
        }
    }
    shipHit() {
        if (this.stats.shipsLeft > 0) {
            this.stats.shipsLeft -= 1;
            this.ship.invincible = true;
            this.ship.invincibleTimer = 0;
        } else {
            this.gameActive = false;
            this.gameOver = true;
            this.gameOverTime = Date.now();
        }
    }
    fireBullet() {
        if (this.bullets.length < 3) {
            const b = new Bullet(this, false);
            b.x = this.ship.x + this.ship.width/2 - b.width/2;
            b.y = this.ship.y;
            this.bullets.push(b);
        }
    }
    collides(obj1, obj2) {
        return obj1.x < obj2.x + obj2.width &&
               obj1.x + obj1.width > obj2.x &&
               obj1.y < obj2.y + obj2.height &&
               obj1.y + obj1.height > obj2.y;
    }
    draw(ctx) {
        ctx.fillStyle = this.settings.bgColor;
        ctx.fillRect(0,0,this.settings.screenWidth, this.settings.screenHeight);
        if (this.gameActive) {
            this.ship.draw(ctx);
            this.bullets.forEach(b => b.draw(ctx));
            this.alienBullets.forEach(b => b.draw(ctx));
            this.aliens.forEach(a => a.draw(ctx));
            // draw score/level/ships
            ctx.fillStyle = '#fff';
            ctx.font = '24px sans-serif';
            ctx.fillText(this.stats.score, this.settings.screenWidth - 100, 30);
            ctx.fillText('Lv'+this.stats.level, this.settings.screenWidth - 100, 60);
            ctx.fillText('Ships: '+this.stats.shipsLeft, 20, this.settings.screenHeight - 20);
        }
        if (this.gameOver) {
            ctx.fillStyle = 'red';
            ctx.font = '80px sans-serif';
            ctx.fillText('GAME OVER', 400, 400);
            if (Date.now() - this.gameOverTime > 3000) {
                this.gameOver = false;
            }
        }
        if (!this.gameActive && !this.gameOver) {
            ctx.fillStyle = '#0f0';
            ctx.font = '48px sans-serif';
            ctx.fillText('PLAY', this.settings.screenWidth/2 - 60, this.settings.screenHeight/2);
        }
    }
}

// bootstrap
const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const game = new Game();

window.addEventListener('keydown', e => {
    switch(e.code) {
        case 'ArrowRight': game.ship.movingRight = true; break;
        case 'ArrowLeft': game.ship.movingLeft = true; break;
        case 'ArrowUp': game.ship.movingUp = true; break;
        case 'ArrowDown': game.ship.movingDown = true; break;
        case 'Space': if (game.gameActive) game.fireBullet(); break;
    }
});
window.addEventListener('keyup', e => {
    switch(e.code) {
        case 'ArrowRight': game.ship.movingRight = false; break;
        case 'ArrowLeft': game.ship.movingLeft = false; break;
        case 'ArrowUp': game.ship.movingUp = false; break;
        case 'ArrowDown': game.ship.movingDown = false; break;
    }
});
canvas.addEventListener('click', () => {
    if (!game.gameActive && !game.gameOver) game.start();
});

function loop() {
    game.update();
    game.draw(ctx);
    requestAnimationFrame(loop);
}

loop();
