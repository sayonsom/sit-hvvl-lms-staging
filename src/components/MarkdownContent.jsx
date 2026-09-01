import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css'; // Import KaTeX CSS
import axios from 'axios';
import Spinner from './Spinner';
import { API_URL } from "../env";
import { safeMarkdownUrl } from '../security/safeMarkdown.mjs';

const MarkdownContent = ({ contentURL }) => {
  const [content, setContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');
  const [retryKey, setRetryKey] = useState(0);

  const apiUrl = API_URL;

  useEffect(() => {
    const loadContent = async () => {
      setIsLoading(true);
      setError('');
      try {
        const signedUrlResponse = await axios.get(`${apiUrl}/generate-signed-url/?blob_name=${contentURL}`);
        const contentResponse = await axios.get(signedUrlResponse.data.url);
        setContent(contentResponse.data);
      } catch (loadError) {
        console.error('Error loading theory content', loadError);
        setContent('');
        setError('Unable to load the theory content. Please retry.');
      } finally {
        setIsLoading(false);
      }
    };

    loadContent();
  }, [apiUrl, contentURL, retryKey]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center">
        <Spinner />
      </div>
    );
  }

  if (error) {
    return (
      <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-5 text-red-900">
        <p>{error}</p>
        <button
          type="button"
          className="mt-3 rounded-md bg-red-700 px-4 py-2 font-semibold text-white hover:bg-red-800"
          onClick={() => setRetryKey((key) => key + 1)}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    // Accordion or collapsible content
    <>
      
      {/* <Disclosure as="div"  className="pt-6">
                {({ open }) => (
                  <>
                    <dt>
                      <DisclosureButton className="flex w-full items-start justify-between text-left text-gray-900">
                        <span className="text-base font-semibold leading-7">Read Theory in Depth</span>
                        <span className="ml-6 flex h-7 items-center">
                          {open ? (
                            <MinusSmallIcon className="h-6 w-6" aria-hidden="true" />
                          ) : (
                            <PlusSmallIcon className="h-6 w-6" aria-hidden="true" />
                          )}
                        </span>
                      </DisclosureButton>
                    </dt>
                    <DisclosurePanel as="dd" className="mt-2 pr-12">
                      <p className="text-base leading-7 text-gray-600">
                        <div className="prose font-sans dark:prose-invert text-justify">
                          <ReactMarkdown
                            children={content}
                            remarkPlugins={[remarkMath]}
                            rehypePlugins={[rehypeKatex]}
                            skipHtml
                            urlTransform={safeMarkdownUrl}
                          />
                        </div>
                      </p>
                    </DisclosurePanel>
                  </>
                )}
              </Disclosure> */}
              <div className="prose max-w-none font-sans text-justify text-base leading-7 text-gray-600 dark:prose-invert">
                <ReactMarkdown
                  remarkPlugins={[remarkMath]}
                  rehypePlugins={[rehypeKatex]}
                  skipHtml
                  urlTransform={safeMarkdownUrl}
                >
                  {content}
                </ReactMarkdown>
              </div>
    </>

    
  );
};

export default MarkdownContent;
