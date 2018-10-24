#-------------------------------------------------------------------#
#                                                                   #
#          Shiny app for visualizing expenses                       #
#                                                                   #
#-------------------------------------------------------------------#

library(shiny)
library(googlesheets)
library(ggplot2)
library(data.table)
library(scales)
library(plotly)

spendings <- gs_key("1hdD1VF34qE_6zPHpSwUys_xTJZy-jajiOSln3aXWSYQ")
spending_data <- setDT(gs_read(spendings))

spending_data[,`:=`(month = substr(Timestamp, 4, 5),
                    year = substr(Timestamp, 7, 10),
                    day = substr(Timestamp, 1, 2))][,
               `:=`(weekday = weekdays(as.Date(paste0(year, "-",
                                                       month, "-",
                                                       day))),
                    posixtime = as.Date(paste0(year, "-",
                                               month, "-",
                                               day))),
                    by=Timestamp]
spending_data[!(`Mit?` %in% c("Lakbér",
                             "Háztartási (vegyszerek, eszközök)",
                             "Számla",
                             "Buli",
                             "Kaja")),
              `Mit?` := "Egyéb"]

spendplot <- ggplot(spending_data[`Ki?`=="András",
                      .(`Mennyiért?`=sum(`Mennyiért?`)),
                      by=.(Hónap=paste0(year, "/", month),
                           `Mit?`)]) +
  geom_col(aes(x=`Hónap`, fill=`Mit?`, group=`Mit?`, y=`Mennyiért?`)) +
  guides(fill=FALSE)

spendplotly <- ggplotly(spendplot)

spendplotly