const mineflayer = require('mineflayer');
const WebSocket = require('ws');

const BOT_NAME = 'M_bot';
const WS_URL = 'ws://localhost:8765';

let currentBot = null;
let ws = null;
let reconnectTimer = null;
let actionRequestInterval = null;
let lastStateSent = 0;
const STATE_INTERVAL_MS = 2000;
const ACTION_REQUEST_INTERVAL = 6000;
const MINECRAFT_RETRY_DELAY = 8000;
const WS_RETRY_DELAY = 5000;

function getSafeInventory(inv) {
    if (!inv || !inv.slots) return [];
    return inv.slots.filter(s => s && s.name).map(s => ({ name: s.name, count: s.count }));
}

function connectMinecraft() {
    if (currentBot) {
        try { currentBot.end(); } catch (e) {}
        currentBot = null;
    }
    currentBot = mineflayer.createBot({ host: 'localhost', port: 25565, username: BOT_NAME });

    currentBot.on('spawn', () => {
        console.log('Bot spawned');
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = null;
    });

    currentBot.on('error', (err) => console.error('Bot error:', err.message));
    currentBot.on('end', (reason) => {
        console.log(`Bot disconnected (${reason || '?'}). Retry in ${MINECRAFT_RETRY_DELAY / 1000}s`);
        if (reconnectTimer) return;
        reconnectTimer = setTimeout(() => {
            reconnectTimer = null;
            connectMinecraft();
        }, MINECRAFT_RETRY_DELAY);
    });

    currentBot.on('chat', (username, msg) => {
        if (username === currentBot.username) return;
        if (msg.startsWith('!action') || msg.startsWith('!event')) {
            const eventText = msg.substring(1);
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'player_event', event: eventText }));
            }
            return;
        }
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'chat', from: username, msg: msg }));
        }
    });
}

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) return;
    ws = new WebSocket(WS_URL);

    ws.on('open', () => {
        console.log('Connected to parent brain');
        if (reconnectTimer) clearTimeout(reconnectTimer);
        reconnectTimer = null;

        if (actionRequestInterval) clearInterval(actionRequestInterval);
        actionRequestInterval = setInterval(() => {
            if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'request_action' }));
            }
        }, ACTION_REQUEST_INTERVAL);
    });

    ws.on('message', (data) => {
        if (!currentBot || !currentBot.entity) return;
        try {
            const cmd = JSON.parse(data);
            const act = cmd.action;
            if (!act || act === 'esc') return;

            if (['forward', 'back', 'left', 'right'].includes(act)) {
                currentBot.setControlState(act, true);
                setTimeout(() => {
                    if (currentBot && currentBot.setControlState) currentBot.setControlState(act, false);
                }, 500);
            } else if (act === 'jump') {
                currentBot.setControlState('jump', true);
                setTimeout(() => {
                    if (currentBot && currentBot.setControlState) currentBot.setControlState('jump', false);
                }, 200);
            } else if (act === 'attack') {
                const e = currentBot.nearestEntity();
                if (e) currentBot.attack(e);
                else currentBot.swingArm();
            } else if (act === 'use') {
                const e = currentBot.nearestEntity();
                if (e) currentBot.activateEntity(e);
                else currentBot.activateItem();
            }
        } catch (e) {
            console.error('Parse error:', e);
        }
    });

    ws.on('close', (code, reason) => {
        console.log(`WebSocket closed (${code}). Retry in ${WS_RETRY_DELAY / 1000}s`);
        if (reconnectTimer) return;
        if (actionRequestInterval) clearInterval(actionRequestInterval);
        reconnectTimer = setTimeout(() => {
            reconnectTimer = null;
            connectWebSocket();
        }, WS_RETRY_DELAY);
    });

    ws.on('error', (err) => console.error('WS error:', err.message));
}

function startStateUpdates() {
    setInterval(() => {
        if (!ws || ws.readyState !== WebSocket.OPEN) return;
        if (!currentBot || !currentBot.entity || !currentBot.entity.position) return;
        const now = Date.now();
        if (now - lastStateSent < STATE_INTERVAL_MS) return;
        lastStateSent = now;
        ws.send(JSON.stringify({
            type: 'state_update',
            position: {
                x: currentBot.entity.position.x,
                y: currentBot.entity.position.y,
                z: currentBot.entity.position.z,
            },
            health: currentBot.health,
            food: currentBot.food,
            inventory: getSafeInventory(currentBot.inventory),
        }));
    }, 500);
}

connectMinecraft();
connectWebSocket();
startStateUpdates();
