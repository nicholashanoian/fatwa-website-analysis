library(ggplot2, dplyr)
library(extrafont)

islamqa <- read.csv("data/islamqa.csv")

cat(as.character(islamqa[1,3]) , "\n")


words <- data.frame(words=c("hello", "my", "name", "is", "nick"), tfidf = c(2,1,0,0,3))



question <- "I have a demand from the bank for 5800 riyals because of a credit card that I had 5 years ago, and I did not pay off what I owe because I found out that it is haraam. I do not know exactly how much I withdrew. They are demanding that I pay this amount in full even though I did not withdraw more than 3500 riyals. Praise be to Allah. So long as you know that you did not withdraw more than 3500 riyals, then you should pay them this amount and no more, if you can do that. If you cannot avoid it – such as if they threaten you with jail etc – then negotiate with them to reduce the extra amount rest as much as you can. You also have to repent greatly from this haraam transaction. And Allah knows best."

vals <- read.csv("./example-tfidf.csv")

word_to_tfidf <- function(word) {
    word <- gsub('[[:punct:] ]+','', word) # delete punctuation
    filtered <- filter(vals, feature == word)
    if (nrow(filtered) == 0) {
        return (0)
    } else {
        return (filtered[1, "tfidf"])
    }
}

df <- data.frame(word=strsplit(question, " "))
colnames(df) <- c("word")
df$word <- as.character(df$word)

df$tfidf <- sapply(df$word, word_to_tfidf)


assign_coords <- function(df) {
    df <- mutate(df, x=0, y=0)
    
    for (i in 1:nrow(df)) {
        width <- 200
        row_height <- 0.1
        char_width <- 3.2
        space_width <- char_width * 1.25
        if (i == 1) {
            df[i, "x"] <- 0
            df[i, "y"] <- 0
            print("here")
        } else {
            past_x <- df[i-1, "x"]
            past_y <- df[i-1, "y"]
            past_word <- df[i-1, "word"]
            
            if (past_x + char_width * (nchar(past_word) + nchar(df[i, "word"])) + space_width > width) {
                df[i, "x"] <- 0
                df[i, "y"] <- past_y - row_height
            } else {
                df[i, "x"] <- past_x + (nchar(past_word)) * char_width + space_width # +1 for space
                df[i, "y"] <- past_y

                if (df[i, "word"] == "Praise") {
                    df[i, "y"] <- past_y - row_height * 2
                    df[i, "x"] <- 0
                }
                }
            }
    }
    # add an extra point out to the right to add space between the paragraphs and the key
    return(rbind(df, data.frame(x=width + 3, y=0, tfidf=0, word="")))

}


df_coords <- assign_coords(df)

ggplot(df_coords, aes(x=x, y=y, fill=tfidf, label=word)) +
    geom_label(hjust=0, color="black", label.size=NA, label.r=unit(0.15, "lines"), size=4, label.padding=unit(0.15, "lines")) +
    scale_fill_gradient(low="white", high="#7ad151") + theme_void() +
    theme(legend.text= element_text(family="Times"),
          legend.title= element_text(family="Times")) +
    labs(fill="TF-IDF")
ggsave("../plots/annotated.pdf", device=cairo_pdf, family="DejaVuSansMono", width=7, height=3.5, dpi="print", units="in")

