import React, { useEffect, useRef, useState } from 'react';

function JobResultModal({ jobResult, onClose }) {
  const modalRef = useRef(null);
  const fetchedRef = useRef(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;

    const ac = new AbortController();
    (async () => {
      try {
        const r = await fetch(`/jobs/${jobResult.job_id}/result`, { signal: ac.signal });
        const data = await r.json();
        setResult(data);
      } catch (e) {
        if (e.name !== 'AbortError') setError(String(e));
      }
    })();
    return () => ac.abort();
  }, [jobResult]);

  useEffect(() => {
    const modalNode = modalRef.current;

    function handleKeyDown(event) {
      if (event.key === 'Escape') {
        onClose();
      }
    }

    function trapFocus(event) {
      if (event.key === 'Tab') {
        const focusableElements = modalNode.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0];
        const lastElement = focusableElements[focusableElements.length - 1];

        if (event.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            event.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            event.preventDefault();
          }
        }
      }
    }

    if (jobResult) {
      document.addEventListener('keydown', handleKeyDown);
      modalNode.addEventListener('keydown', trapFocus);
      document.body.style.overflow = 'hidden';
      // Focus the close button when the modal opens
      const closeButton = modalNode.querySelector('#ok-btn');
      if (closeButton) {
        closeButton.focus();
      }
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      if (modalNode) {
        modalNode.removeEventListener('keydown', trapFocus);
      }
      document.body.style.overflow = 'unset';
    };
  }, [jobResult, onClose]);

  if (!jobResult) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center"
      role="dialog"
      aria-modal="true"
    >
      <div
        ref={modalRef}
        className="relative mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white"
      >
        <div className="mt-3 text-center">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Job Result</h3>
          <div className="mt-2 px-7 py-3">
            <pre
              className="whitespace-pre-wrap break-words"
              style={{
                fontFamily: 'monospace',
                textAlign: 'left',
              }}
            >
              {error ? error : JSON.stringify(result, null, 2)}
            </pre>
          </div>
          <div className="items-center px-4 py-3">
            <button
              id="ok-btn"
              className="px-4 py-2 bg-blue-500 text-white text-base font-medium rounded-md w-full shadow-sm hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-300"
              onClick={onClose}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default JobResultModal;
