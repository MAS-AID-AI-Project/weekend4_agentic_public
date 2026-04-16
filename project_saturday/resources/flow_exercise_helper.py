"""
Helper module to generate interactive flow exercises for the notebook.
Students don't need to see this code - it's imported and used automatically.
"""

from IPython.display import HTML

def display_exercise_1():
    """Display Exercise 1: TechNova Customer Support Flow"""
    html_content = """
    <style>
        .flow-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .flow-box {
            background: white;
            border: 3px solid transparent;
            border-radius: 12px;
            padding: 25px 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 15px;
            font-weight: 600;
            position: relative;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .flow-box:hover:not(.selected):not(.distractor-hint) {
            background-color: #f0f7ff;
            border-color: #4CAF50;
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 8px 15px rgba(76, 175, 80, 0.3);
        }
        .flow-box.selected {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border-color: #45a049;
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
        }
        .flow-box.distractor-hint {
            background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%);
            color: #c62828;
            border-color: #f44336;
            animation: shake 0.5s;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        .flow-box .order-number {
            display: none;
            position: absolute;
            top: -10px;
            right: -10px;
            background: #FF5722;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 16px;
            font-weight: bold;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .flow-box.selected .order-number {
            display: flex;
        }
        .flow-box .emoji {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .flow-box .hint-text {
            display: none;
            font-size: 12px;
            margin-top: 8px;
            font-weight: 500;
        }
        .flow-box.distractor-hint .hint-text {
            display: block;
        }
        .controls {
            margin: 25px 0;
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        .btn {
            padding: 12px 28px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 700;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .btn-check {
            background: linear-gradient(135deg, #2196F3 0%, #0b7dda 100%);
            color: white;
        }
        .btn-check:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(33, 150, 243, 0.4);
        }
        .btn-reset {
            background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
            color: white;
        }
        .btn-reset:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(244, 67, 54, 0.4);
        }
        .feedback {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: 500;
            display: none;
            font-size: 15px;
            line-height: 1.6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .feedback.success {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724;
            border-left: 5px solid #28a745;
            display: block;
        }
        .feedback.error {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            color: #721c24;
            border-left: 5px solid #dc3545;
            display: block;
        }
    </style>

    <div id="exercise1">
        <div class="flow-container" id="flow1">
            <div class="flow-box" data-id="1" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">📥</div>
                <div>Incoming Mailbox</div>
            </div>
            <div class="flow-box" data-id="7" data-type="distractor">
                <div class="order-number"></div>
                <div class="emoji">📣</div>
                <div>Marketing DB</div>
                <div class="hint-text">⚠️ Wrong context - need support data!</div>
            </div>
            <div class="flow-box" data-id="3" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">📚</div>
                <div>Technical Manuals (RAG)</div>
            </div>
            <div class="flow-box" data-id="5" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">📤</div>
                <div>Outbox</div>
            </div>
            <div class="flow-box" data-id="2" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">🤖</div>
                <div>LLM Agent</div>
            </div>
            <div class="flow-box" data-id="6" data-type="distractor">
                <div class="order-number"></div>
                <div class="emoji">🔍</div>
                <div>Web Search</div>
                <div class="hint-text">⚠️ Not precise enough to give you what you are looking for! You also risk leaking private data!</div>
            </div>
            <div class="flow-box" data-id="4" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">💾</div>
                <div>Customer Contract DB</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-check" onclick="checkAnswer1()">Check Answer</button>
            <button class="btn btn-reset" onclick="resetFlow1()">Reset</button>
        </div>

        <div class="feedback" id="feedback1"></div>
    </div>

    <script>
        let selectedOrder1 = [1];
        let selectionMap1 = {1: 1};
        const correctOrder1 = [1, 2, 3, 4, 5];

        // Pre-select trigger immediately
        (function() {
            const triggerBox = document.querySelector('#flow1 .flow-box[data-id="1"]');
            if (triggerBox) {
                triggerBox.classList.add('selected');
                triggerBox.querySelector('.order-number').textContent = '1';
            }
        })();

        document.querySelectorAll('#flow1 .flow-box').forEach(box => {
            box.addEventListener('click', function() {
                const id = parseInt(this.getAttribute('data-id'));
                const type = this.getAttribute('data-type');

                // Handle distractor boxes
                if (type === 'distractor') {
                    this.classList.add('distractor-hint');
                    setTimeout(() => {
                        this.classList.remove('distractor-hint');
                    }, 2000);
                    return;
                }

                // Handle correct boxes
                if (this.classList.contains('selected')) {
                    // Don't allow unselecting the trigger (id=1)
                    if (id === 1) return;

                    const orderNum = selectionMap1[id];
                    delete selectionMap1[id];

                    document.querySelectorAll('#flow1 .flow-box[data-type="correct"]').forEach(b => {
                        b.classList.remove('selected');
                        b.querySelector('.order-number').textContent = '';
                    });

                    selectedOrder1 = selectedOrder1.filter((val, idx) => idx !== orderNum - 1);
                    selectionMap1 = {};

                    selectedOrder1.forEach((itemId, idx) => {
                        const targetBox = document.querySelector(`#flow1 .flow-box[data-id="${itemId}"]`);
                        if (targetBox) {
                            targetBox.classList.add('selected');
                            targetBox.querySelector('.order-number').textContent = idx + 1;
                            selectionMap1[itemId] = idx + 1;
                        }
                    });
                } else {
                    selectedOrder1.push(id);
                    const orderNum = selectedOrder1.length;
                    this.classList.add('selected');
                    this.querySelector('.order-number').textContent = orderNum;
                    selectionMap1[id] = orderNum;
                }
            });
        });

        function resetFlow1() {
            selectedOrder1 = [1];
            selectionMap1 = {1: 1};
            document.querySelectorAll('#flow1 .flow-box').forEach(box => {
                box.classList.remove('selected');
                box.classList.remove('distractor-hint');
                box.querySelector('.order-number').textContent = '';
            });
            // Re-select trigger
            const triggerBox = document.querySelector('#flow1 .flow-box[data-id="1"]');
            if (triggerBox) {
                triggerBox.classList.add('selected');
                triggerBox.querySelector('.order-number').textContent = '1';
            }
            const feedback = document.getElementById('feedback1');
            feedback.style.display = 'none';
            feedback.className = 'feedback';
        }

        function checkAnswer1() {
            const feedback = document.getElementById('feedback1');

            if (selectedOrder1.length < 2) {
                feedback.className = 'feedback error';
                feedback.style.display = 'block';
                feedback.textContent = '❌ Please select more boxes to create your flow!';
                return;
            }

            const isCorrect = JSON.stringify(selectedOrder1) === JSON.stringify(correctOrder1);

            if (isCorrect) {
                feedback.className = 'feedback success';
                feedback.style.display = 'block';
                feedback.textContent = '✅ Excellent! The correct flow is: Incoming Mailbox → LLM Agent → Technical Manuals (RAG) → Customer Contract DB → Outbox. The system receives the support email, the LLM interprets it, retrieves technical documentation and customer contract information, then generates and sends an accurate response.';
            } else {
                feedback.className = 'feedback error';
                feedback.style.display = 'block';
                feedback.textContent = '❌ Not quite right. Think about: What does the LLM need to look up to answer technical questions? Where is the customer\\'s support plan stored? How does the response get back to the customer? Try again!';
            }
        }
    </script>
    """
    return HTML(html_content)


def display_exercise_2():
    """Display Exercise 2: Sales Dashboard Flow"""
    html_content = """
    <style>
        .flow-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 20px;
            padding: 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        .flow-box {
            background: white;
            border: 3px solid transparent;
            border-radius: 12px;
            padding: 25px 15px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            font-size: 15px;
            font-weight: 600;
            position: relative;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            min-height: 100px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        .flow-box:hover:not(.selected):not(.distractor-hint) {
            background-color: #f0f7ff;
            border-color: #4CAF50;
            transform: translateY(-5px) scale(1.05);
            box-shadow: 0 8px 15px rgba(76, 175, 80, 0.3);
        }
        .flow-box.selected {
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
            color: white;
            border-color: #45a049;
            transform: scale(1.05);
            box-shadow: 0 8px 20px rgba(76, 175, 80, 0.4);
        }
        .flow-box.distractor-hint {
            background: linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%);
            color: #c62828;
            border-color: #f44336;
            animation: shake 0.5s;
        }
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        .flow-box .order-number {
            display: none;
            position: absolute;
            top: -10px;
            right: -10px;
            background: #FF5722;
            color: white;
            width: 32px;
            height: 32px;
            border-radius: 50%;
            font-size: 16px;
            font-weight: bold;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3);
        }
        .flow-box.selected .order-number {
            display: flex;
        }
        .flow-box .emoji {
            font-size: 32px;
            margin-bottom: 8px;
        }
        .flow-box .hint-text {
            display: none;
            font-size: 12px;
            margin-top: 8px;
            font-weight: 500;
        }
        .flow-box.distractor-hint .hint-text {
            display: block;
        }
        .controls {
            margin: 25px 0;
            display: flex;
            gap: 15px;
            justify-content: center;
        }
        .btn {
            padding: 12px 28px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 15px;
            font-weight: 700;
            transition: all 0.2s;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .btn-check {
            background: linear-gradient(135deg, #2196F3 0%, #0b7dda 100%);
            color: white;
        }
        .btn-check:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(33, 150, 243, 0.4);
        }
        .btn-reset {
            background: linear-gradient(135deg, #f44336 0%, #da190b 100%);
            color: white;
        }
        .btn-reset:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(244, 67, 54, 0.4);
        }
        .feedback {
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            font-weight: 500;
            display: none;
            font-size: 15px;
            line-height: 1.6;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .feedback.success {
            background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
            color: #155724;
            border-left: 5px solid #28a745;
            display: block;
        }
        .feedback.error {
            background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
            color: #721c24;
            border-left: 5px solid #dc3545;
            display: block;
        }
    </style>

    <div id="exercise2">
        <div class="flow-container" id="flow2">
            <div class="flow-box" data-id="1" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">💬</div>
                <div>User Prompt</div>
            </div>
            <div class="flow-box" data-id="3" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">🤖</div>
                <div>LLM Agent</div>
            </div>
            <div class="flow-box" data-id="4" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">💾</div>
                <div>Secure Database (SQL)</div>
            </div>
            <div class="flow-box" data-id="7" data-type="distractor">
                <div class="order-number"></div>
                <div class="emoji">🎨</div>
                <div>Creative Image Gen (DALL-E)</div>
                <div class="hint-text">⚠️ Need data charts, not creative art!</div>
            </div>
            <div class="flow-box" data-id="6" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">📊</div>
                <div>Plotting Tool</div>
            </div>
            <div class="flow-box" data-id="8" data-type="distractor">
                <div class="order-number"></div>
                <div class="emoji">📰</div>
                <div>Public Financial News</div>
                <div class="hint-text">⚠️ Need internal sales data, not news!</div>
            </div>
            <div class="flow-box" data-id="2" data-type="correct">
                <div class="order-number"></div>
                <div class="emoji">🔐</div>
                <div>Authentication Layer</div>
            </div>
        </div>

        <div class="controls">
            <button class="btn btn-check" onclick="checkAnswer2()">Check Answer</button>
            <button class="btn btn-reset" onclick="resetFlow2()">Reset</button>
        </div>

        <div class="feedback" id="feedback2"></div>
    </div>

    <script>
        let selectedOrder2 = [1];
        let selectionMap2 = {1: 1};
        const correctOrder2 = [1, 3, 2, 4, 6];

        // Pre-select trigger immediately
        (function() {
            const triggerBox = document.querySelector('#flow2 .flow-box[data-id="1"]');
            if (triggerBox) {
                triggerBox.classList.add('selected');
                triggerBox.querySelector('.order-number').textContent = '1';
            }
        })();

        document.querySelectorAll('#flow2 .flow-box').forEach(box => {
            box.addEventListener('click', function() {
                const id = parseInt(this.getAttribute('data-id'));
                const type = this.getAttribute('data-type');

                // Handle distractor boxes
                if (type === 'distractor') {
                    this.classList.add('distractor-hint');
                    setTimeout(() => {
                        this.classList.remove('distractor-hint');
                    }, 2000);
                    return;
                }

                // Handle correct boxes
                if (this.classList.contains('selected')) {
                    // Don't allow unselecting the trigger (id=1)
                    if (id === 1) return;

                    const orderNum = selectionMap2[id];
                    delete selectionMap2[id];

                    document.querySelectorAll('#flow2 .flow-box[data-type="correct"]').forEach(b => {
                        b.classList.remove('selected');
                        b.querySelector('.order-number').textContent = '';
                    });

                    selectedOrder2 = selectedOrder2.filter((val, idx) => idx !== orderNum - 1);
                    selectionMap2 = {};

                    selectedOrder2.forEach((itemId, idx) => {
                        const targetBox = document.querySelector(`#flow2 .flow-box[data-id="${itemId}"]`);
                        if (targetBox) {
                            targetBox.classList.add('selected');
                            targetBox.querySelector('.order-number').textContent = idx + 1;
                            selectionMap2[itemId] = idx + 1;
                        }
                    });
                } else {
                    selectedOrder2.push(id);
                    const orderNum = selectedOrder2.length;
                    this.classList.add('selected');
                    this.querySelector('.order-number').textContent = orderNum;
                    selectionMap2[id] = orderNum;
                }
            });
        });

        function resetFlow2() {
            selectedOrder2 = [1];
            selectionMap2 = {1: 1};
            document.querySelectorAll('#flow2 .flow-box').forEach(box => {
                box.classList.remove('selected');
                box.classList.remove('distractor-hint');
                box.querySelector('.order-number').textContent = '';
            });
            // Re-select trigger
            const triggerBox = document.querySelector('#flow2 .flow-box[data-id="1"]');
            if (triggerBox) {
                triggerBox.classList.add('selected');
                triggerBox.querySelector('.order-number').textContent = '1';
            }
            const feedback = document.getElementById('feedback2');
            feedback.style.display = 'none';
            feedback.className = 'feedback';
        }

        function checkAnswer2() {
            const feedback = document.getElementById('feedback2');

            if (selectedOrder2.length < 2) {
                feedback.className = 'feedback error';
                feedback.style.display = 'block';
                feedback.textContent = '❌ Please select more boxes to create your flow!';
                return;
            }

            const isCorrect = JSON.stringify(selectedOrder2) === JSON.stringify(correctOrder2);

            if (isCorrect) {
                feedback.className = 'feedback success';
                feedback.style.display = 'block';
                feedback.textContent = '✅ Perfect! The correct flow is: User Prompt → Authentication Layer → LLM Agent → Database (SQL) → Data Formatter → Plotting Tool. The VP is authenticated, the LLM interprets the request and generates a SQL query, data is retrieved and formatted, then visualized as a bar chart.';
            } else {
                feedback.className = 'feedback error';
                feedback.style.display = 'block';
                feedback.textContent = '❌ Not quite. Consider: What happens first for security? How does the LLM get sales data? What prepares the data for visualization? What actually creates the chart? Try again!';
            }
        }
    </script>
    """
    return HTML(html_content)
