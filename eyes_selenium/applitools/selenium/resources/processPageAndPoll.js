// @applitools/dom-snapshot@1.2.4
function __processPageAndPoll() {
  var processPageAndPoll = (function () {
  'use strict';

  // This code was copied and modified from https://github.com/beatgammit/base64-js/blob/bf68aaa277/index.js
  // License: https://github.com/beatgammit/base64-js/blob/bf68aaa277d9de7007cc0c58279c411bb10670ac/LICENSE

  function arrayBufferToBase64(ab) {
    const lookup = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'.split('');

    const uint8 = new Uint8Array(ab);
    const len = uint8.length;
    const extraBytes = len % 3; // if we have 1 byte left, pad 2 bytes
    const parts = [];
    const maxChunkLength = 16383; // must be multiple of 3

    let tmp;

    // go through the array every three bytes, we'll deal with trailing stuff later
    for (let i = 0, len2 = len - extraBytes; i < len2; i += maxChunkLength) {
      parts.push(encodeChunk(i, i + maxChunkLength > len2 ? len2 : i + maxChunkLength));
    }

    // pad the end with zeros, but make sure to not forget the extra bytes
    if (extraBytes === 1) {
      tmp = uint8[len - 1];
      parts.push(lookup[tmp >> 2] + lookup[(tmp << 4) & 0x3f] + '==');
    } else if (extraBytes === 2) {
      tmp = (uint8[len - 2] << 8) + uint8[len - 1];
      parts.push(lookup[tmp >> 10] + lookup[(tmp >> 4) & 0x3f] + lookup[(tmp << 2) & 0x3f] + '=');
    }

    return parts.join('');

    function tripletToBase64(num) {
      return (
        lookup[(num >> 18) & 0x3f] +
        lookup[(num >> 12) & 0x3f] +
        lookup[(num >> 6) & 0x3f] +
        lookup[num & 0x3f]
      );
    }

    function encodeChunk(start, end) {
      let tmp;
      const output = [];
      for (let i = start; i < end; i += 3) {
        tmp = ((uint8[i] << 16) & 0xff0000) + ((uint8[i + 1] << 8) & 0xff00) + (uint8[i + 2] & 0xff);
        output.push(tripletToBase64(tmp));
      }
      return output.join('');
    }
  }

  var arrayBufferToBase64_1 = arrayBufferToBase64;

  function extractLinks(doc = document) {
    const srcsetUrls = [...doc.querySelectorAll('img[srcset],source[srcset]')]
      .map(srcsetEl =>
        srcsetEl
          .getAttribute('srcset')
          .split(',')
          .map(str => str.trim().split(/\s+/)[0]),
      )
      .reduce((acc, urls) => acc.concat(urls), []);

    const srcUrls = [...doc.querySelectorAll('img[src],source[src]')].map(srcEl =>
      srcEl.getAttribute('src'),
    );

    const hrefUrls = [...doc.querySelectorAll('image')]
      .map(hrefEl => hrefEl.getAttribute('href') || hrefEl.getAttribute('xlink:href'))
      .filter(Boolean);

    const cssUrls = [...doc.querySelectorAll('link[rel="stylesheet"]')].map(link =>
      link.getAttribute('href'),
    );

    const videoPosterUrls = [...doc.querySelectorAll('video[poster]')].map(videoEl =>
      videoEl.getAttribute('poster'),
    );

    return [...srcsetUrls, ...srcUrls, ...hrefUrls, ...cssUrls, ...videoPosterUrls];
  }

  var extractLinks_1 = extractLinks;

  /* eslint-disable no-use-before-define */

  function domNodesToCdt(docNode) {
    const NODE_TYPES = {
      ELEMENT: 1,
      TEXT: 3,
      DOCUMENT: 9,
      DOCUMENT_TYPE: 10,
      DOCUMENT_FRAGMENT_NODE: 11,
    };

    const domNodes = [
      {
        nodeType: NODE_TYPES.DOCUMENT,
      },
    ];
    domNodes[0].childNodeIndexes = childrenFactory(domNodes, docNode.childNodes);
    return domNodes;

    function childrenFactory(domNodes, elementNodes) {
      if (!elementNodes || elementNodes.length === 0) return null;

      const childIndexes = [];
      elementNodes.forEach(elementNode => {
        const index = elementNodeFactory(domNodes, elementNode);
        if (index !== null) {
          childIndexes.push(index);
        }
      });

      return childIndexes;
    }

    function elementNodeFactory(domNodes, elementNode) {
      let node, manualChildNodeIndexes;
      const {nodeType} = elementNode;
      if ([NODE_TYPES.ELEMENT, NODE_TYPES.DOCUMENT_FRAGMENT_NODE].includes(nodeType)) {
        if (elementNode.nodeName !== 'SCRIPT') {
          if (
            elementNode.nodeName === 'STYLE' &&
            elementNode.sheet &&
            elementNode.sheet.cssRules.length
          ) {
            domNodes.push({
              nodeType: NODE_TYPES.TEXT,
              nodeValue: [...elementNode.sheet.cssRules].map(rule => rule.cssText).join(''),
            });
            manualChildNodeIndexes = [domNodes.length - 1];
          }

          node = {
            nodeType: nodeType,
            nodeName: elementNode.nodeName,
            attributes: nodeAttributes(elementNode).map(key => {
              let value = elementNode.attributes[key].value;
              const name = elementNode.attributes[key].localName;

              if (/^blob:/.test(value)) {
                value = value.replace(/^blob:/, '');
              } else if (
                elementNode.nodeName === 'IFRAME' &&
                name === 'src' &&
                !elementNode.contentDocument &&
                !value.match(/^\s*data:/)
              ) {
                value = '';
              }
              return {
                name,
                value,
              };
            }),
            childNodeIndexes:
              manualChildNodeIndexes ||
              (elementNode.childNodes.length
                ? childrenFactory(domNodes, elementNode.childNodes)
                : []),
          };

          if (elementNode.shadowRoot) {
            node.shadowRootIndex = elementNodeFactory(domNodes, elementNode.shadowRoot);
          }

          if (elementNode.checked && !elementNode.attributes.checked) {
            node.attributes.push({name: 'checked', value: 'checked'});
          }
          if (
            elementNode.value !== undefined &&
            elementNode.attributes.value === undefined &&
            elementNode.tagName === 'INPUT'
          ) {
            node.attributes.push({name: 'value', value: elementNode.value});
          }
        } else {
          node = {
            nodeType: NODE_TYPES.ELEMENT,
            nodeName: 'SCRIPT',
            attributes: nodeAttributes(elementNode)
              .map(key => ({
                name: elementNode.attributes[key].localName,
                value: elementNode.attributes[key].value,
              }))
              .filter(attr => attr.name !== 'src'),
            childNodeIndexes: [],
          };
        }
      } else if (nodeType === NODE_TYPES.TEXT) {
        node = {
          nodeType: NODE_TYPES.TEXT,
          nodeValue: elementNode.nodeValue,
        };
      } else if (nodeType === NODE_TYPES.DOCUMENT_TYPE) {
        node = {
          nodeType: NODE_TYPES.DOCUMENT_TYPE,
          nodeName: elementNode.nodeName,
        };
      }

      if (node) {
        domNodes.push(node);
        return domNodes.length - 1;
      } else {
        // console.log(`Unknown nodeType: ${nodeType}`);
        return null;
      }

      function nodeAttributes({attributes = {}}) {
        return Object.keys(attributes).filter(k => attributes[k].localName);
      }
    }
  }

  var domNodesToCdt_1 = domNodesToCdt;
  var NODE_TYPES = {
    ELEMENT: 1,
    TEXT: 3,
    DOCUMENT: 9,
    DOCUMENT_TYPE: 10,
  };
  domNodesToCdt_1.NODE_TYPES = NODE_TYPES;

  function extractFrames(doc = document) {
    return [...doc.querySelectorAll('iframe[src]:not([src=""])')]
      .map(srcEl => {
        try {
          const contentDoc = srcEl.contentDocument;
          return (
            contentDoc &&
            /^https?:$/.test(contentDoc.location.protocol) &&
            contentDoc.defaultView &&
            contentDoc.defaultView.frameElement &&
            contentDoc
          );
        } catch (err) {
          //for CORS frames
        }
      })
      .filter(x => !!x);
  }

  var extractFrames_1 = extractFrames;

  function uniq(arr) {
    const result = [];
    new Set(arr).forEach(v => v && result.push(v));
    return result;
  }

  var uniq_1 = uniq;

  function aggregateResourceUrlsAndBlobs(resourceUrlsAndBlobsArr) {
    return resourceUrlsAndBlobsArr.reduce(
      ({resourceUrls: allResourceUrls, blobsObj: allBlobsObj}, {resourceUrls, blobsObj}) => ({
        resourceUrls: uniq_1(allResourceUrls.concat(resourceUrls)),
        blobsObj: Object.assign(allBlobsObj, blobsObj),
      }),
      {resourceUrls: [], blobsObj: {}},
    );
  }

  var aggregateResourceUrlsAndBlobs_1 = aggregateResourceUrlsAndBlobs;

  function makeGetResourceUrlsAndBlobs({processResource, aggregateResourceUrlsAndBlobs}) {
    return function getResourceUrlsAndBlobs(doc, baseUrl, urls) {
      return Promise.all(
        urls.map(url => processResource(url, doc, baseUrl, getResourceUrlsAndBlobs.bind(null, doc))),
      ).then(resourceUrlsAndBlobsArr => aggregateResourceUrlsAndBlobs(resourceUrlsAndBlobsArr));
    };
  }

  var getResourceUrlsAndBlobs = makeGetResourceUrlsAndBlobs;

  function filterInlineUrl(absoluteUrl) {
    return /^(blob|https?):/.test(absoluteUrl);
  }

  var filterInlineUrl_1 = filterInlineUrl;

  function absolutizeUrl(url, absoluteUrl) {
    return new URL(url, absoluteUrl).href;
  }

  var absolutizeUrl_1 = absolutizeUrl;

  function makeProcessResource({
    fetchUrl,
    findStyleSheetByUrl,
    extractResourcesFromStyleSheet,
    isSameOrigin,
    cache = {},
  }) {
    return function processResource(absoluteUrl, doc, baseUrl, getResourceUrlsAndBlobs) {
      return cache[absoluteUrl] || (cache[absoluteUrl] = doProcessResource(absoluteUrl));

      function doProcessResource(url) {
        return fetchUrl(url)
          .catch(e => {
            if (probablyCORS(e, url)) {
              return {probablyCORS: true, url};
            } else {
              throw e;
            }
          })
          .then(({url, type, value, probablyCORS}) => {
            if (probablyCORS) {
              return {resourceUrls: [url]};
            }
            const result = {blobsObj: {[url]: {type, value}}};
            if (/text\/css/.test(type)) {
              const styleSheet = findStyleSheetByUrl(url, doc);
              if (!styleSheet) {
                return result;
              }
              const resourceUrls = extractResourcesFromStyleSheet(styleSheet, doc.defaultView)
                .map(resourceUrl => absolutizeUrl_1(resourceUrl, url.replace(/^blob:/, '')))
                .filter(filterInlineUrl_1);
              return getResourceUrlsAndBlobs(baseUrl, resourceUrls).then(
                ({resourceUrls, blobsObj}) => ({
                  resourceUrls,
                  blobsObj: Object.assign(blobsObj, {[url]: {type, value}}),
                }),
              );
            } else {
              return result;
            }
          })
          .catch(err => {
            console.log('[dom-snapshot] error while fetching', url, err);
            return {};
          });
      }

      function probablyCORS(err, url) {
        const msgCORS = err.message && err.message.includes('Failed to fetch');
        const nameCORS = err.name && err.name.includes('TypeError');
        return msgCORS && nameCORS && !isSameOrigin(url, baseUrl);
      }
    };
  }

  var processResource = makeProcessResource;

  /* global window */

  function fetchUrl(url, fetch = window.fetch) {
    return fetch(url, {cache: 'force-cache', credentials: 'same-origin'}).then(resp =>
      resp.arrayBuffer().then(buff => ({
        url,
        type: resp.headers.get('Content-Type'),
        value: buff,
      })),
    );
  }

  var fetchUrl_1 = fetchUrl;

  function makeFindStyleSheetByUrl({styleSheetCache}) {
    return function findStyleSheetByUrl(url, doc) {
      return styleSheetCache[url] || [...doc.styleSheets].find(styleSheet => styleSheet.href === url);
    };
  }

  var findStyleSheetByUrl = makeFindStyleSheetByUrl;

  function getUrlFromCssText(cssText) {
    const re = /url\((?!['"]?:)['"]?([^'")]*)['"]?\)/g;
    const ret = [];
    let result;
    while ((result = re.exec(cssText)) !== null) {
      ret.push(result[1]);
    }
    return ret;
  }

  var getUrlFromCssText_1 = getUrlFromCssText;

  // NOTE this code is very similar to the node part of visual-grid-client, but there is a different related to the browser's cssom with import rules
  function makeExtractResourcesFromStyleSheet({styleSheetCache}) {
    return function extractResourcesFromStyleSheet(styleSheet, win = window) {
      return uniq_1(
        [...(styleSheet.cssRules || [])].reduce((acc, rule) => {
          if (rule instanceof win.CSSImportRule) {
            styleSheetCache[rule.styleSheet.href] = rule.styleSheet;
            return acc.concat(rule.href);
          } else if (rule instanceof win.CSSFontFaceRule) {
            return acc.concat(getUrlFromCssText_1(rule.style.getPropertyValue('src')));
          } else if (rule instanceof win.CSSSupportsRule || rule instanceof win.CSSMediaRule) {
            return acc.concat(extractResourcesFromStyleSheet(rule));
          } else if (rule instanceof win.CSSStyleRule) {
            for (let i = 0, ii = rule.style.length; i < ii; i++) {
              const urls = getUrlFromCssText_1(rule.style.getPropertyValue(rule.style[i]));
              urls.length && (acc = acc.concat(urls));
            }
          }
          return acc;
        }, []),
      );
    };
  }

  var extractResourcesFromStyleSheet = makeExtractResourcesFromStyleSheet;

  function extractResourceUrlsFromStyleAttrs(cdt) {
    return cdt.reduce((acc, node) => {
      if (node.nodeType === 1) {
        const styleAttr =
          node.attributes && node.attributes.find(attr => attr.name.toUpperCase() === 'STYLE');

        if (styleAttr) acc = acc.concat(getUrlFromCssText_1(styleAttr.value));
      }
      return acc;
    }, []);
  }

  var extractResourceUrlsFromStyleAttrs_1 = extractResourceUrlsFromStyleAttrs;

  function makeExtractResourceUrlsFromStyleTags(extractResourcesFromStyleSheet) {
    return function extractResourceUrlsFromStyleTags(doc) {
      return uniq_1(
        [...doc.getElementsByTagName('style')].reduce((resourceUrls, styleEl) => {
          const styleSheet = [...doc.styleSheets].find(
            styleSheet => styleSheet.ownerNode === styleEl,
          );
          return resourceUrls.concat(extractResourcesFromStyleSheet(styleSheet, doc.defaultView));
        }, []),
      );
    };
  }

  var extractResourceUrlsFromStyleTags = makeExtractResourceUrlsFromStyleTags;

  function isSameOrigin(url, baseUrl) {
    const blobOrData = /^(blob|data):/;
    if (blobOrData.test(url)) return true;
    if (blobOrData.test(baseUrl)) return false;

    const {origin} = new URL(url, baseUrl);
    const {origin: baseOrigin} = new URL(baseUrl);
    return origin === baseOrigin;
  }

  var isSameOrigin_1 = isSameOrigin;

  function processPage(doc = document) {
    const styleSheetCache = {};
    const extractResourcesFromStyleSheet$$1 = extractResourcesFromStyleSheet({styleSheetCache});
    const findStyleSheetByUrl$$1 = findStyleSheetByUrl({styleSheetCache});
    const processResource$$1 = processResource({
      fetchUrl: fetchUrl_1,
      findStyleSheetByUrl: findStyleSheetByUrl$$1,
      extractResourcesFromStyleSheet: extractResourcesFromStyleSheet$$1,
      absolutizeUrl: absolutizeUrl_1,
      isSameOrigin: isSameOrigin_1,
    });

    const getResourceUrlsAndBlobs$$1 = getResourceUrlsAndBlobs({
      processResource: processResource$$1,
      aggregateResourceUrlsAndBlobs: aggregateResourceUrlsAndBlobs_1,
    });

    const extractResourceUrlsFromStyleTags$$1 = extractResourceUrlsFromStyleTags(
      extractResourcesFromStyleSheet$$1,
    );

    return doProcessPage(doc);

    function doProcessPage(doc) {
      const frameElement = doc.defaultView && doc.defaultView.frameElement;
      const url = frameElement ? frameElement.src : doc.location.href;

      const cdt = domNodesToCdt_1(doc);

      const links = uniq_1(
        extractLinks_1(doc)
          .concat(extractResourceUrlsFromStyleAttrs_1(cdt))
          .concat(extractResourceUrlsFromStyleTags$$1(doc)),
      )
        .map(absolutizeThisUrl)
        .filter(filterInlineUrlsIfExisting);

      const resourceUrlsAndBlobsPromise = getResourceUrlsAndBlobs$$1(doc, url, links);

      const frameDocs = extractFrames_1(doc);
      const processFramesPromise = frameDocs.map(doProcessPage);

      return Promise.all([resourceUrlsAndBlobsPromise, ...processFramesPromise]).then(
        ([{resourceUrls, blobsObj}, ...framesResults]) => ({
          cdt,
          url,
          resourceUrls,
          blobs: blobsObjToArray(blobsObj),
          frames: framesResults,
          srcAttr: frameElement ? frameElement.getAttribute('src') : undefined,
        }),
      );

      function absolutizeThisUrl(someUrl) {
        try {
          return absolutizeUrl_1(someUrl, url);
        } catch (err) {
          // can't do anything with a non-absolute url
        }
      }
    }
  }

  function blobsObjToArray(blobsObj) {
    return Object.keys(blobsObj).map(blobUrl =>
      Object.assign(
        {
          url: blobUrl.replace(/^blob:/, ''),
        },
        blobsObj[blobUrl],
      ),
    );
  }

  function filterInlineUrlsIfExisting(absoluteUrl) {
    return absoluteUrl && filterInlineUrl_1(absoluteUrl);
  }

  var processPage_1 = processPage;

  function processPageAndSerialize(doc) {
    return processPage_1(doc).then(serializeFrame);
  }

  function serializeFrame(frame) {
    frame.blobs = frame.blobs.map(({url, type, value}) => ({
      url,
      type,
      value: arrayBufferToBase64_1(value),
    }));
    frame.frames.forEach(serializeFrame);
    return frame;
  }

  var processPageAndSerialize_1 = processPageAndSerialize;

  const EYES_NAME_SPACE = '__EYES__APPLITOOLS__';

  function processPageAndPoll(doc) {
    if (!window[EYES_NAME_SPACE]) {
      window[EYES_NAME_SPACE] = {};
    }
    if (!window[EYES_NAME_SPACE].processPageAndSerializeResult) {
      window[EYES_NAME_SPACE].processPageAndSerializeResult = {
        status: 'WIP',
        value: null,
        error: null,
      };
      processPageAndSerialize_1(doc)
        .then(r => ((resultObject.status = 'SUCCESS'), (resultObject.value = r)))
        .catch(e => ((resultObject.status = 'ERROR'), (resultObject.error = e.message)));
    }

    const resultObject = window[EYES_NAME_SPACE].processPageAndSerializeResult;
    if (resultObject.status === 'SUCCESS') {
      window[EYES_NAME_SPACE].processPageAndSerializeResult = null;
    }

    return JSON.stringify(resultObject);
  }

  var processPageAndPoll_1 = processPageAndPoll;

  return processPageAndPoll_1;

}());

  return processPageAndPoll.apply(this, arguments);
}