# classroom_pgg

This application can be used to run Public Goods Games (PGGs) in the classroom. The application allows for multiple treatments, including cheap talk (chat) It was developed for use in [this](https://studiegids.vu.nl/en/2019-2020/courses/AM_468020) course. 
The idea is that you start with a one-shot public goods game without any additional features. Every week (or class) you can add a feature, by using oTree Rooms to adjust the configurations.
You can analyze the within-subjects results at the end of the course, and compare the average contributions under different parameters. 

To install the app to your local oTree directory, copy the folder 'classroom_pgg' to your oTree Django project and extend the session configurations in your ```settings.py``` at the root of the oTree directory:

```
SESSION_CONFIGS = [
    dict(	
        name='classroom_pgg',
        display_name="Experiment",
        num_demo_participants=3,
        players_per_group=3,
        num_rounds=1,
        efficiency_factor=1.6,
        punishment_factor=3,
        app_sequence=['classroom_pgg'],
        cheap_talk=False,
        punishment=False,
        threshold=0,
    )
                  ]
```


## Treatments

* One-shot game versus sequential game (change `num_rounds`)
* Cheap talk (set `cheap_talk` to `True` to add a chatbox to the Contribution page)
* Punishment (set `punishment` to `True` to add a Deduction page)
* Threshold (set `threshold` to any number above 0)

## Credits

Punishment page from [Philipp Chapkovski](https://github.com/chapkovski/fehr-and-gaechter). 
Threshold feature adapted from [BowieG](https://github.com/BowieG/oTree-PGG).
