function cleanString(str) {
    // Remove line breaks at the end of the string
    str = str.replace(/\s+$/, '');

    // Remove repeating spaces and replace with one space
    str = str.replace(/\s+/g, ' ');

    // Remove repeating line breaks and replace with one line break
    str = str.replace(/[\r\n]{2,}/g, '\n');

    return str;
}

function get_json() {
    let json = {
        ad_name: cleanString(document.evaluate('//div[@class="wrapper_pre"][1]//pre', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null).snapshotItem(0).textContent),
        ad_descr: cleanString(document.evaluate('//div[@class="wrapper_pre"][3]//pre', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null).snapshotItem(0).textContent),
        messages: [],
        answers: {
            all: [],
            correct: undefined,
        },
    };

    const msgs_elem = document.evaluate("//div[@class='messages']//div[contains(@class, 'row')]/div[@class='message text']", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
    for (let i = 0; i < msgs_elem.snapshotLength; i++) {
        const msg = cleanString(msgs_elem.snapshotItem(i).textContent);
        let from = 'buyer';
        if (msgs_elem.snapshotItem(i).parentNode.classList.value.includes('seller'))
            from = 'seller';
        json.messages.push({
            msg : msg,
            from: from,
        });
    }

    const answers_elems = document.evaluate('//div[@class="answer" or @class="answer checked"]', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null)
    for (let i = 0; i < answers_elems.snapshotLength; i++) {
        const textNodes = Array.from(answers_elems.snapshotItem(i).childNodes).filter(node => node.nodeType === Node.TEXT_NODE);
        const textContent = cleanString(textNodes.map(node => node.textContent.trim()).join(' '));
        json.answers.all.push(cleanString(textContent));
    }

    return json;
}

function downloadJSON(json, filename) {
   const blob = new Blob([JSON.stringify(json)], {type: 'application/json'});
   const url = URL.createObjectURL(blob);
   const link = document.createElement('a');
   link.href = url;
   link.download = filename;
   document.body.appendChild(link);
   link.click();
   document.body.removeChild(link);
   URL.revokeObjectURL(url);
}

const targetNode = document.querySelector('.progress_bar > * > *');
const config = { characterData: true, attributes: false, childList: false, subtree: true }

const callback = mutations => {
    mutations.forEach(mutation => {
        const quest_counter = targetNode.innerText;
        console.log("Mutation observing:", quest_counter);

        const que_number = parseInt(quest_counter.split(' ')[2]);

        const elements = document.evaluate('//div[@class="answer"]', document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        for (let i = 0; i < elements.snapshotLength; i++) {
            const element = elements.snapshotItem(i);
            element.addEventListener('click', () => {
                const textNodes = Array.from(element.childNodes).filter(node => node.nodeType === Node.TEXT_NODE);
                const textContent = cleanString(textNodes.map(node => node.textContent.trim()).join(' '));

                const res_json = get_json();
                res_json.answers.correct = textContent;
                if (textContent == 'Да') {
                    let opt_msg = document.evaluate("//div[@class='text']", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
                    opt_msg = cleanString(opt_msg.snapshotItem(0).textContent);
                    if (opt_msg != '')
                        res_json.answers.correct = {correct: res_json.answers.correct, opt_msg: opt_msg};
                }
                const today = new Date();
                const day = String(today.getDate()).padStart(2, '0');
                const month = String(today.getMonth() + 1).padStart(2, '0');

                const file_name = `question_${que_number}_${day}_${month}.json`;
                res_json.oid = String(que_number)
                downloadJSON(res_json, file_name);
                console.log(`Question ${que_number}. Answer: ${textContent}. Built JSON and download file ${file_name}.`);
            });
        }
    });
}

const observer = new MutationObserver(callback);

observer.observe(targetNode, config);