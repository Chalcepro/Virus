const mineflayer = require('mineflayer');
const bot = mineflayer.createBot({ host: 'localhost', port: 25565, username: 'TestBot' });
bot.on('spawn', () => console.log('SUCCESS'));
bot.on('error', (e) => console.log('ERROR:', e));
