FROM artemqaapplitools/chrome-docker:latest

RUN git clone git://github.com/yyuu/pyenv.git /home/project/.pyenv

ENV HOME  /home/project
ENV PYENV_ROOT $HOME/.pyenv
ENV PATH $PYENV_ROOT/shims:$PYENV_ROOT/bin:$PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends make build-essential libssl-dev zlib1g-dev libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev

RUN pyenv install 3.8.5 \
    && pyenv global 3.8.5
