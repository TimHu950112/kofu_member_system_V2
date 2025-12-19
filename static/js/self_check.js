let phoneNumber = '';
let inactivityTimer = null;

// 重置閒置計時器
function resetInactivityTimer() {
    // 清除舊的計時器
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
    }

    // 只有當有輸入內容時才啟動計時器
    if (phoneNumber.length > 0) {
        inactivityTimer = setTimeout(() => {
            clearAll();
        }, 15000); // 15秒
    }
}

// 添加數字
function addNumber(num) {
    if (phoneNumber.length < 10) {
        phoneNumber += num;
        updateDisplay();
        playClickSound();
        resetInactivityTimer();

        // 添加動畫效果
        const display = document.getElementById('phoneDisplay');
        display.classList.add('animate-pulse');
        setTimeout(() => display.classList.remove('animate-pulse'), 300);
    }
}

// 刪除最後一個數字
function deleteNumber() {
    if (phoneNumber.length > 0) {
        phoneNumber = phoneNumber.slice(0, -1);
        updateDisplay();
        playClickSound();
        resetInactivityTimer();
    }
}

// 清除所有
function clearAll() {
    // 清除計時器
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
        inactivityTimer = null;
    }

    if (phoneNumber.length > 0 || document.getElementById('resultMessage').style.display !== 'none') {
        phoneNumber = '';
        updateDisplay();
        document.getElementById('resultMessage').style.display = 'none';
        playClickSound();
    }
}

// 更新顯示
function updateDisplay() {
    const display = document.getElementById('phoneDisplay');
    if (phoneNumber.length === 0) {
        display.textContent = '請輸入電話';
        display.style.color = '#999';
    } else {
        display.textContent = phoneNumber;
        display.style.color = '#333';
    }
}

// 查詢會員
async function checkMember() {
    const resultDiv = document.getElementById('resultMessage');

    // 檢查電話號碼長度
    if (phoneNumber.length !== 8 && phoneNumber.length !== 10) {
        showResult('請輸入8位或10位電話號碼', 'error');
        playSound('error');
        resetInactivityTimer();
        return;
    }

    // 停止計時器（查詢後不自動清除）
    if (inactivityTimer) {
        clearTimeout(inactivityTimer);
        inactivityTimer = null;
    }

    try {
        // 呼叫API查詢會員
        const response = await fetch(`/api/customer-check?phone=${phoneNumber}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();
        console.log('API回應:', data);

        if (response.ok && data.customers && data.customers.length > 0) {
            // 檢查會員是否有效
            const customer = data.customers[0];
            const currentYear = new Date().getFullYear();

            if (customer.permanent_status || customer.active_year === currentYear) {
                // 會員有效
                showResult('會員您好', 'success');
                playSound('success');
                speak('會員您好');
            } else {
                // 會員失效
                showResult('查無會員', 'error');
                playSound('error');
                speak('查無會員');
            }
        } else {
            // 查無會員
            showResult('查無會員', 'error');
            playSound('error');
            speak('查無會員');
        }

        // 查詢完成後清除電話號碼
        phoneNumber = '';
        updateDisplay();
    } catch (error) {
        console.error('查詢錯誤:', error);
        showResult('系統錯誤，請稍後再試', 'error');
        playSound('error');
    }
}

// 顯示結果訊息
function showResult(message, type) {
    const resultDiv = document.getElementById('resultMessage');
    resultDiv.textContent = message;
    resultDiv.className = 'result-message ' + (type === 'success' ? 'result-success' : 'result-error');
    resultDiv.style.display = 'block';

    // 添加動畫效果
    resultDiv.classList.add('animate-pulse');
    setTimeout(() => resultDiv.classList.remove('animate-pulse'), 500);
}

// 播放音效
function playSound(type) {
    const sound = document.getElementById(type === 'success' ? 'successSound' : 'errorSound');
    sound.currentTime = 0;
    sound.play().catch(err => console.log('音效播放失敗:', err));
}

// 播放按鈕點擊音效
function playClickSound() {
    const sound = document.getElementById('clickSound');
    if (sound) {
        sound.currentTime = 0;
        sound.play().catch(err => console.log('按鈕音效播放失敗:', err));
    }
}

// 語音朗讀
function speak(text) {
    // 檢查瀏覽器是否支援語音合成
    if ('speechSynthesis' in window) {
        // 停止之前的朗讀
        window.speechSynthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'zh-TW'; // 設定為繁體中文
        utterance.rate = 0.9; // 朗讀速度
        utterance.pitch = 1; // 音調
        utterance.volume = 1; // 音量

        window.speechSynthesis.speak(utterance);
    } else {
        console.log('瀏覽器不支援語音合成');
    }
}

// 鍵盤支援
document.addEventListener('keydown', function(event) {
    if (event.key >= '0' && event.key <= '9') {
        addNumber(event.key);
    } else if (event.key === 'Backspace') {
        deleteNumber();
    } else if (event.key === 'Delete' || event.key === 'Escape') {
        clearAll();
    } else if (event.key === 'Enter') {
        checkMember();
    }
});
