import sys
from prepare import PrepareData, combine_all_data, create_summary_table
from models import CasesModel, DeathsModel, general_logistic_shift

N_TRAIN = 60  
N_SMOOTH = 15  
N_PRED = 56    
L_N_MIN = 5    
L_N_MAX = 50   

LAG = 15     
PERIOD = 30  

if __name__ == "__main__":
    if len(sys.argv) == 1:
        last_date = None
    elif len(sys.argv) == 2:
        last_date = sys.argv[1]
    else:
        raise TypeError(

        )
    data = PrepareData().run()
    cm = CasesModel(
        model=general_logistic_shift,
        data=data,
        last_date=last_date,
        n_train=N_TRAIN,
        n_smooth=N_SMOOTH,
        n_pred=N_PRED,
        L_n_min=L_N_MIN,
        L_n_max=L_N_MAX,
    )
    cm.run()

    dm = DeathsModel(data=data, last_date=last_date, cm=cm, lag=15, period=30)
    dm.run()

    df_all = combine_all_data(cm, dm)
    create_summary_table(df_all, cm.last_date)
