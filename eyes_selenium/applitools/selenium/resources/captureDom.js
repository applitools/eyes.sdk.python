// @applitools/dom-snapshot@7.0.10
function __captureDom() {
  var captureDom = (function () {
  'use strict';

  const styleProps = [
    'background-repeat',
    'background-origin',
    'background-position',
    'background-color',
    'background-image',
    'background-size',
    'border-width',
    'border-color',
    'border-style',
    'color',
    'display',
    'font-size',
    'line-height',
    'margin',
    'opacity',
    'overflow',
    'padding',
    'visibility',
  ];

  const rectProps = ['width', 'height', 'top', 'left'];

  const ignoredTagNames = ['HEAD', 'SCRIPT'];

  var defaultDomProps = {
    styleProps,
    rectProps,
    ignoredTagNames,
  };

  const bgImageRe = /url\((?!['"]?:)['"]?([^'")]*)['"]?\)/;

  function getBackgroundImageUrl(cssText) {
    const match = cssText ? cssText.match(bgImageRe) : undefined;
    return match ? match[1] : match;
  }

  var getBackgroundImageUrl_1 = getBackgroundImageUrl;

  const psetTimeout = t =>
    new Promise(res => {
      setTimeout(res, t);
    });

  async function getImageSizes({bgImages, timeout = 5000, Image = window.Image}) {
    return (await Promise.all(
      Array.from(bgImages).map(url =>
        Promise.race([
          new Promise(resolve => {
            const img = new Image();
            img.onload = () => resolve({url, width: img.naturalWidth, height: img.naturalHeight});
            img.onerror = () => resolve();
            img.src = url;
          }),
          psetTimeout(timeout),
        ]),
      ),
    )).reduce((images, curr) => {
      if (curr) {
        images[curr.url] = {width: curr.width, height: curr.height};
      }
      return images;
    }, {});
  }

  var getImageSizes_1 = getImageSizes;

  function genXpath(el) {
    if (!el.ownerDocument) return ''; // this is the document node

    let xpath = '',
      currEl = el,
      doc = el.ownerDocument,
      frameElement = doc.defaultView.frameElement;
    while (currEl !== doc) {
      xpath = `${currEl.tagName}[${getIndex(currEl)}]/${xpath}`;
      currEl = currEl.parentNode;
    }
    if (frameElement) {
      xpath = `${genXpath(frameElement)},${xpath}`;
    }
    return xpath.replace(/\/$/, '');
  }

  function getIndex(el) {
    return (
      Array.prototype.filter
        .call(el.parentNode.childNodes, node => node.tagName === el.tagName)
        .indexOf(el) + 1
    );
  }

  var genXpath_1 = genXpath;

  function absolutizeUrl(url, absoluteUrl) {
    return new URL(url, absoluteUrl).href;
  }

  var absolutizeUrl_1 = absolutizeUrl;

  function makeGetBundledCssFromCssText({
    parseCss,
    CSSImportRule,
    absolutizeUrl,
    fetchCss,
    unfetchedToken,
  }) {
    return async function getBundledCssFromCssText(cssText, resourceUrl) {
      let unfetchedResources;
      let bundledCss = '';

      try {
        const styleSheet = parseCss(cssText);
        for (const rule of Array.from(styleSheet.cssRules)) {
          if (rule instanceof CSSImportRule) {
            const nestedUrl = absolutizeUrl(rule.href, resourceUrl);
            const nestedResource = await fetchCss(nestedUrl);
            if (nestedResource !== undefined) {
              const {
                bundledCss: nestedCssText,
                unfetchedResources: nestedUnfetchedResources,
              } = await getBundledCssFromCssText(nestedResource, nestedUrl);

              nestedUnfetchedResources && (unfetchedResources = new Set(nestedUnfetchedResources));
              bundledCss = `${nestedCssText}${bundledCss}`;
            } else {
              unfetchedResources = new Set([nestedUrl]);
              bundledCss = `\n${unfetchedToken}${nestedUrl}${unfetchedToken}`;
            }
          }
        }
      } catch (ex) {
        console.log(`error during getBundledCssFromCssText, resourceUrl=${resourceUrl}`, ex);
      }

      bundledCss = `${bundledCss}${getCss(cssText, resourceUrl)}`;

      return {
        bundledCss,
        unfetchedResources,
      };
    };
  }

  function getCss(newText, url) {
    return `\n/** ${url} **/\n${newText}`;
  }

  var getBundledCssFromCssText = makeGetBundledCssFromCssText;

  function parseCss(styleContent) {
    var doc = document.implementation.createHTMLDocument(''),
      styleElement = doc.createElement('style');
    styleElement.textContent = styleContent;
    // the style will only be parsed once it is added to a document
    doc.body.appendChild(styleElement);

    return styleElement.sheet;
  }

  var parseCss_1 = parseCss;

  function makeFetchCss(fetch) {
    return async function fetchCss(url) {
      try {
        const response = await fetch(url);
        if (response.ok) {
          return await response.text();
        }
        console.log('/failed to fetch (status ' + response.status + ') css from: ' + url + '/');
      } catch (err) {
        console.log('/failed to fetch (error ' + err.toString() + ') css from: ' + url + '/');
      }
    };
  }

  var fetchCss = makeFetchCss;

  function makeExtractCssFromNode({fetchCss, absolutizeUrl}) {
    return async function extractCssFromNode(node, baseUrl) {
      let cssText, resourceUrl, isUnfetched;
      if (isStyleElement(node)) {
        cssText = Array.from(node.childNodes)
          .map(node => node.nodeValue)
          .join('');
        resourceUrl = baseUrl;
      } else if (isLinkToStyleSheet(node)) {
        resourceUrl = absolutizeUrl(getHrefAttr(node), baseUrl);
        cssText = await fetchCss(resourceUrl);
        if (cssText === undefined) {
          isUnfetched = true;
        }
      }
      return {cssText, resourceUrl, isUnfetched};
    };
  }

  function isStyleElement(node) {
    return node.nodeName && node.nodeName.toUpperCase() === 'STYLE';
  }

  function getHrefAttr(node) {
    const attr = Array.from(node.attributes).find(attr => attr.name.toLowerCase() === 'href');
    return attr && attr.value;
  }

  function isLinkToStyleSheet(node) {
    return (
      node.nodeName &&
      node.nodeName.toUpperCase() === 'LINK' &&
      node.attributes &&
      Array.from(node.attributes).find(
        attr => attr.name.toLowerCase() === 'rel' && attr.value.toLowerCase() === 'stylesheet',
      )
    );
  }

  var extractCssFromNode = makeExtractCssFromNode;

  function makeCaptureNodeCss({extractCssFromNode, getBundledCssFromCssText, unfetchedToken}) {
    return async function captureNodeCss(node, baseUrl) {
      const {resourceUrl, cssText, isUnfetched} = await extractCssFromNode(node, baseUrl);

      let unfetchedResources;
      let bundledCss = '';
      if (cssText) {
        const {
          bundledCss: nestedCss,
          unfetchedResources: nestedUnfetched,
        } = await getBundledCssFromCssText(cssText, resourceUrl);

        bundledCss += nestedCss;
        unfetchedResources = new Set(nestedUnfetched);
      } else if (isUnfetched) {
        bundledCss += `${unfetchedToken}${resourceUrl}${unfetchedToken}`;
        unfetchedResources = new Set([resourceUrl]);
      }
      return {bundledCss, unfetchedResources};
    };
  }

  var captureNodeCss = makeCaptureNodeCss;

  const NODE_TYPES = {
    ELEMENT: 1,
    TEXT: 3,
  };
  const API_VERSION = '1.0.0';

  async function captureFrame(
    {styleProps, rectProps, ignoredTagNames} = defaultDomProps,
    doc = document,
  ) {
    const start = Date.now();
    const unfetchedResources = new Set();
    const iframeCors = [];
    const iframeToken = '@@@@@';
    const unfetchedToken = '#####';
    const separator = '-----';

    const fetchCss$$1 = fetchCss(fetch);
    const getBundledCssFromCssText$$1 = getBundledCssFromCssText({
      parseCss: parseCss_1,
      CSSImportRule,
      fetchCss: fetchCss$$1,
      absolutizeUrl: absolutizeUrl_1,
      unfetchedToken,
    });
    const extractCssFromNode$$1 = extractCssFromNode({fetchCss: fetchCss$$1, absolutizeUrl: absolutizeUrl_1});
    const captureNodeCss$$1 = captureNodeCss({
      extractCssFromNode: extractCssFromNode$$1,
      getBundledCssFromCssText: getBundledCssFromCssText$$1,
      unfetchedToken,
    });

    // Note: Change the API_VERSION when changing json structure.
    const capturedFrame = await doCaptureFrame(doc);
    capturedFrame.version = API_VERSION;

    const iframePrefix = iframeCors.length ? `${iframeCors.join('\n')}\n` : '';
    const unfetchedPrefix = unfetchedResources.size
      ? `${Array.from(unfetchedResources).join('\n')}\n`
      : '';
    const metaPrefix = JSON.stringify({
      separator,
      cssStartToken: unfetchedToken,
      cssEndToken: unfetchedToken,
      iframeStartToken: `"${iframeToken}`,
      iframeEndToken: `${iframeToken}"`,
    });
    const ret = `${metaPrefix}\n${unfetchedPrefix}${separator}\n${iframePrefix}${separator}\n${JSON.stringify(
    capturedFrame,
  )}`;
    console.log('[captureFrame]', Date.now() - start);
    return ret;

    function filter(x) {
      return !!x;
    }

    function notEmptyObj(obj) {
      return Object.keys(obj).length ? obj : undefined;
    }

    function captureTextNode(node) {
      return {
        tagName: '#text',
        text: node.textContent,
      };
    }

    async function doCaptureFrame(frameDoc) {
      const bgImages = new Set();
      let bundledCss = '';
      const ret = await captureNode(frameDoc.documentElement);
      ret.css = bundledCss;
      ret.images = await getImageSizes_1({bgImages});
      return ret;

      async function captureNode(node) {
        const {bundledCss: nodeCss, unfetchedResources: nodeUnfetched} = await captureNodeCss$$1(
          node,
          frameDoc.location.href,
        );
        bundledCss += nodeCss;
        if (nodeUnfetched) for (const elem of nodeUnfetched) unfetchedResources.add(elem);

        switch (node.nodeType) {
          case NODE_TYPES.TEXT: {
            return captureTextNode(node);
          }
          case NODE_TYPES.ELEMENT: {
            const tagName = node.tagName.toUpperCase();
            if (tagName === 'IFRAME') {
              return await iframeToJSON(node);
            } else {
              return await await elementToJSON(node);
            }
          }
          default: {
            return null;
          }
        }
      }

      async function elementToJSON(el) {
        const childNodes = (await Promise.all(
          Array.prototype.map.call(el.childNodes, captureNode),
        )).filter(filter);

        const tagName = el.tagName.toUpperCase();
        if (ignoredTagNames.indexOf(tagName) > -1) return null;

        const computedStyle = window.getComputedStyle(el);
        const boundingClientRect = el.getBoundingClientRect();

        const style = {};
        for (const p of styleProps) style[p] = computedStyle.getPropertyValue(p);

        const rect = {};
        for (const p of rectProps) rect[p] = boundingClientRect[p];

        const attributes = Array.from(el.attributes)
          .map(a => ({key: a.name, value: a.value}))
          .reduce((obj, attr) => {
            obj[attr.key] = attr.value;
            return obj;
          }, {});

        const bgImage = getBackgroundImageUrl_1(computedStyle.getPropertyValue('background-image'));
        if (bgImage) {
          bgImages.add(bgImage);
        }

        return {
          tagName,
          style: notEmptyObj(style),
          rect: notEmptyObj(rect),
          attributes: notEmptyObj(attributes),
          childNodes,
        };
      }

      async function iframeToJSON(el) {
        const obj = await elementToJSON(el);
        try {
          if (el.contentDocument) {
            obj.childNodes = [await doCaptureFrame(el.contentDocument)];
          } else {
            const xpath = genXpath_1(el);
            iframeCors.push(xpath);
            obj.childNodes = [`${iframeToken}${xpath}${iframeToken}`];
          }
        } catch (ex) {
          console.log('error in iframeToJSON', ex);
        }
        return obj;
      }
    }
  }

  var captureFrame_1 = captureFrame;

  return captureFrame_1;

}());

  return captureDom.apply(this, arguments);
}