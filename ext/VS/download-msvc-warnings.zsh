!#/usr/bin/zsh

# Download the list of warnings from Microsoft Docs

curl -O https://raw.githubusercontent.com/MicrosoftDocs/cpp-docs/master/docs/error-messages/compiler-warnings/compiler-warnings-by-compiler-version.md

for i in 4000 4200 4400 4600 4800;
do
    echo $i
    curl -O https://raw.githubusercontent.com/MicrosoftDocs/cpp-docs/master/docs/error-messages/compiler-warnings/compiler-warnings-c$i-through-c$((i+199)).md
done
