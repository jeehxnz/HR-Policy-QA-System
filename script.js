// Navigation links
document.getElementById('logo-link').addEventListener('click', (e) => {
  if (window.location.pathname.endsWith('index.html') || window.location.pathname === '/') {
    e.preventDefault();
  } else {
    window.location.href = 'index.html';
  }
});

const goToQueryBtn = document.querySelector('.hero-section .cta-button');
if (goToQueryBtn) {
  goToQueryBtn.addEventListener('click', () => {
    window.location.href = 'query.html';
  });
}

const askQuestionNavButton = document.querySelector('.header-content .nav-button:not(.current-page)');
if (askQuestionNavButton) {
  askQuestionNavButton.addEventListener('click', () => {
    window.location.href = 'query.html';
  });
}

const submitBtn = document.getElementById('submit-question');
const questionBox = document.getElementById('question-box');

const answerModal = document.getElementById('answer-modal');
const modalAnswerTextDiv = document.getElementById('modal-answer-text');
const modalSourceInfoDiv = document.getElementById('modal-source-info');
const modalSourceListUl = document.getElementById('modal-source-list');
const closeButton = document.querySelector('.close-button');

const loadingStateDiv = document.getElementById('loading-state');
const errorStateDiv = document.getElementById('error-state');
const errorTextDiv = document.getElementById('error-text');
const feedbackSection = document.getElementById('feedback-section');
const feedbackButtons = document.querySelectorAll('.feedback-button');

function displayMainState(state) {
    loadingStateDiv.style.display = 'none';
    errorStateDiv.style.display = 'none';
    feedbackSection.style.display = 'none';
    submitBtn.disabled = false;

    if (state === 'loading') {
        loadingStateDiv.style.display = 'block';
        submitBtn.disabled = true;
    } else if (state === 'error') {
        errorStateDiv.style.display = 'block';
        submitBtn.disabled = false;
    } else if (state === 'initial') {
    }
}

function renderMarkdown(text) {
    let html = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.split('\n').map(line => {
        if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
            return `<li>${line.trim().substring(2)}</li>`;
        }
        return line;
    }).join('\n');

    if (html.includes('<li>')) {
        const lines = html.split('\n');
        let listHtml = '';
        let inList = false;

        lines.forEach(line => {
            if (line.trim().startsWith('<li>')) {
                if (!inList) {
                    listHtml += '<ul>';
                    inList = true;
                }
                listHtml += line;
            } else {
                if (inList) {
                    listHtml += '</ul>';
                    inList = false;
                }
                listHtml += line + '\n';
            }
        });
        if (inList) {
             listHtml += '</ul>';
        }
        html = listHtml.trim();
    }

    return html;
}


if (submitBtn && questionBox && answerModal && modalAnswerTextDiv && modalSourceInfoDiv && modalSourceListUl && loadingStateDiv && errorStateDiv && errorTextDiv && feedbackSection && closeButton) {

  submitBtn.addEventListener('click', async () => {
    const question = questionBox.value.trim();
    if (!question) {
      alert('Please type a question before submitting.');
      return;
    }

    displayMainState('loading');
    errorTextDiv.textContent = '';

    try {
      const response = await fetch('http://127.0.0.1:5000/ask', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: question }),
      });

      if (!response.ok) {
        let errorDetails = `HTTP status: ${response.status}`;
        try {
             const errorData = await response.json();
             if (errorData && errorData.error) {
                 errorDetails += `, Details: ${errorData.error}`;
             }
        } catch (parseError) {
            console.error("Failed to parse error response body:", parseError);
        }
        errorTextDiv.textContent = `Error communicating with the server: ${errorDetails}. Please check the backend terminal for more details.`;
        displayMainState('error');
        console.error("API call failed:", response.status, response.statusText);

      } else {
        const result = await response.json();

        if (result && result.error) {
          errorTextDiv.textContent = `Backend reported an error: ${result.error}`;
          displayMainState('error');
        } else if (result && result.answer) {
          modalAnswerTextDiv.innerHTML = renderMarkdown(result.answer);

          modalSourceListUl.innerHTML = '';
          const sourceFiles = new Set();
          if (result.source_metadata && result.source_metadata.length > 0) {
              result.source_metadata.forEach(meta => {
                  const filename = meta.source_file.replace('_cleaned.txt', '').replace('_chunks.json', '');
                  sourceFiles.add(filename);
              });

              if (sourceFiles.size > 0) {
                  sourceFiles.forEach(fileName => {
                      const li = document.createElement('li');
                      li.textContent = fileName;
                      modalSourceListUl.appendChild(li);
                  });
                  modalSourceInfoDiv.style.display = 'block';
              } else {
                   modalSourceInfoDiv.style.display = 'none';
              }
          } else {
               modalSourceInfoDiv.style.display = 'none';
          }

          answerModal.style.display = 'block';
          displayMainState('initial');
          feedbackSection.style.display = 'block';

        } else {
            errorTextDiv.textContent = "Received an unexpected response format from the server.";
            displayMainState('error');
            console.error("Unexpected backend response JSON:", result);
        }
      }

    } catch (error) {
      console.error("Fetch or processing error:", error);
      errorTextDiv.textContent = `An unexpected error occurred: ${error.message}. Please check your network connection and backend server.`;
      displayMainState('error');
    }
  });

    questionBox.addEventListener('keypress', function(event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            submitBtn.click();
        }
    });

  closeButton.addEventListener('click', () => {
    answerModal.style.display = 'none';
    questionBox.value = ''; 
    questionBox.focus(); 
  });

  window.addEventListener('click', (event) => {
    if (event.target == answerModal) {
      answerModal.style.display = 'none';
      questionBox.value = ''; 
      questionBox.focus(); 
    }
  });

  feedbackButtons.forEach(button => {
    button.addEventListener('click', () => {
      const feedback = button.getAttribute('data-feedback');
      console.log(`User provided feedback: ${feedback}`);
      alert(`Thank you for your feedback! We received: ${feedback}`);
    });
  });
}
